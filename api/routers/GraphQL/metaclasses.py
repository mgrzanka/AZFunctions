from sqlmodel import SQLModel, func, col, select
from sqlalchemy.sql.selectable import Select
import typing
import types
import strawberry


def is_optional(type_: typing.Any) -> bool:
    origin = typing.get_origin(type_)
    args = typing.get_args(type_)
    return (origin is typing.Union or origin is types.UnionType) and type(None) in args


def get_real_type(type_: typing.Any) -> typing.Any:
    args = typing.get_args(type_)
    if not args:
        return type_
    for arg in args:
        if arg is not type(None):
            return arg
    return type_


class QueryWrapper:
    def __init__(self, query: Select, model: typing.Type[SQLModel]):
        self.query = query
        self.model = model


class BaseTypesMetaclass(type):
    def __new__(cls, name, bases, attrs):
        model_class: SQLModel = attrs.get('model', None)
        allowed_types = attrs.get('allowed_types', None)
        annotation_for_field_func: typing.Callable = attrs.get(
            'annotation_for_field_func',
            lambda key, field: field.annotation or field.type_
        )

        if model_class is None:
            raise Exception(
                "Define model that contains SQLModel class, allowed_types set and annotation_for_field_func func"
            )

        annotations = attrs.get('__annotations__', {})

        fields_source = getattr(model_class, "model_fields", None) or model_class.__fields__
        for field_name, field_info in fields_source.items():
            if field_name in annotations:
                continue

            raw_type = getattr(field_info, "annotation", None) or getattr(field_info, "type_", None)
            real_type = get_real_type(raw_type)

            if allowed_types is None or real_type in allowed_types:
                target_type = annotation_for_field_func(field_name, field_info)
                annotations[field_name] = target_type
                if is_optional(target_type):
                    attrs[field_name] = None

        attrs['__annotations__'] = annotations
        
        if 'model' in attrs: del attrs['model']
        if 'allowed_types' in attrs: del attrs['allowed_types']
        if 'annotation_for_field_func' in attrs: del attrs['annotation_for_field_func']
        
        return super().__new__(cls, name, bases, attrs)


class AgregateTypeMetaclass(type):
    def __new__(cls, name, bases, attrs):
        model_class = attrs.get('model')
        if not model_class:
            return super().__new__(cls, name, bases, attrs)

        numeric_fields: list[str] = []
        fields_source = getattr(model_class, "model_fields", None) or model_class.__fields__
        
        for field_name, field_info in fields_source.items():
            raw_type = getattr(field_info, "annotation", None) or getattr(field_info, "type_", None)
            real_type = get_real_type(raw_type)
            if real_type in [int, float]:
                numeric_fields.append(field_name)

        def count_resolver(root: QueryWrapper, info: strawberry.Info) -> int:
            db_session = info.context['db_session']
            count_subquery = select(func.count("*")).select_from(root.query.subquery())
            result = db_session.exec(count_subquery).one_or_none()
            return int(result) if result else 0

        def create_aggregate_resolver(func_sqlalchemy, column_name):
            def resolver(root: QueryWrapper, info: strawberry.Info) -> float:
                db_session = info.context['db_session']
                field_col = getattr(root.model, column_name)
                agg_query = root.query.with_only_columns(func_sqlalchemy(col(field_col)))
                result = db_session.exec(agg_query).one_or_none()
                return float(result) if result else 0.0
            return resolver

        def create_avg_resolver(column_name: str):
            def avg_resolver(root: QueryWrapper, info: strawberry.Info) -> float:
                total_sum = create_aggregate_resolver(func.sum, column_name)(root, info)
                total_count = count_resolver(root, info)
                if total_count == 0:
                    return 0
                return total_sum / total_count
            return avg_resolver

        operations = {
            "sum": {"func": func.sum, "is_sql_func": True},
            "max": {"func": func.max, "is_sql_func": True},
            "min": {"func": func.min, "is_sql_func": True},
            "avg": {"func": create_avg_resolver, "is_sql_func": False}
        }
        for op_name, func_dict in operations.items():
            op_fields = {}
            for field in numeric_fields:
                resolver = create_aggregate_resolver(func_dict["func"], field) \
                    if func_dict["is_sql_func"] \
                    else func_dict["func"](field)
                op_fields[field] = strawberry.field(resolver=resolver)

            AggregateDynamicClass = strawberry.type(
                type(f"{name}{op_name.capitalize()}", (object,), op_fields)
            )
            def pass_through(root: QueryWrapper) -> typing.Optional[AggregateDynamicClass]:
                return root     # type: ignore
            attrs[op_name] = strawberry.field(resolver=pass_through)
        
        attrs["count"] = strawberry.field(resolver=count_resolver)

        return super().__new__(cls, name, bases, attrs)
