import strawberry
import typing
import inspect
import sqlalchemy
from enum import Enum
from sqlmodel import Session, select, SQLModel

import api.models as models
from api.routers.GraphQL.metaclasses import QueryWrapper, BaseTypesMetaclass, AgregateTypeMetaclass


@strawberry.type
class GroupKey:
    name: str
    value: str


@strawberry.enum
class OrderByDirection(Enum):
    asc = "asc"
    desc = "desc"


class QueryFactory:
    def create_query(self):
        query_fields = {}

        for name, obj in inspect.getmembers(models, inspect.isclass):
            if issubclass(obj, SQLModel) and obj is not SQLModel:
                print(f"Registering class {name}...")
                fields = self._create_resolvers_ad_types(name, obj)
                query_fields.update(fields)

        Query = strawberry.type(type("Query", (object,), query_fields))
        return Query

    def _create_resolvers_ad_types(self, model_name: str, model: typing.Type[SQLModel]):
        EntityType, GroupResultType, OrderByType = self._create_model_types(model_name, model)

        def base_class_query(
                info: strawberry.Info,
                order_by: typing.Optional[typing.List[OrderByType]] = None,
                offset: typing.Optional[int] = None,
                limit: typing.Optional[int] = None
            ) -> typing.List[EntityType]:
                db_session: Session = info.context['db_session']
                query = select(model)

                if order_by:
                    for order_by_component in order_by:
                        for field, direction in vars(order_by_component).items():
                            if direction and direction == OrderByDirection.desc:
                                query = query.order_by(getattr(model, field).desc())
                            elif direction:
                                query = query.order_by(getattr(model, field))                    

                if offset:
                    query = query.offset(offset)
                if limit:
                    query = query.limit(limit)
                result = db_session.exec(query).all()        
                return result    #type: ignore

        def grouped_query( 
            info: strawberry.Info, 
            group_by: typing.List[str]
        ) -> typing.List[GroupResultType]:
            if len(group_by) == 0:
                raise Exception("Provide at least one field to group by")

            db_session = info.context['db_session']
            joins_needed = []
            joined_paths = set()

            group_columns = []
            for field_name in group_by:
                field_name = field_name.lower()
                if model_name.lower() in field_name:
                    raise Exception("You can't join the same model")
                current_model = model
                path_prefix = ""

                field_parts = field_name.split(".")
                for field_part in field_parts[:-1]:
                    mapper = sqlalchemy.inspect(current_model)
                    if mapper is None or field_part not in mapper.relationships:
                        raise Exception(f"Relationship '{field_part}' not found in model {current_model.__name__}")

                    relationship_attr = mapper.relationships[field_part]
                    target_model = relationship_attr.mapper.class_
                    path_key = f"{path_prefix}.{field_part}"
                    
                    if path_key not in joined_paths:
                        joins_needed.append(target_model)
                        joined_paths.add(path_key)

                    current_model = target_model
                    path_prefix = path_key

                if not hasattr(current_model, field_parts[-1]):
                    raise Exception(f"Field {field_name} not found in model")
                group_columns.append(getattr(current_model, field_parts[-1]))

            query = select(model)
            for join_model in joins_needed:
                query = query.join(join_model)
            from_clause = query.get_final_froms()[0]
            group_by_query = (
                select(*group_columns)
                .select_from(from_clause)
                .group_by(*group_columns)
            )

            results = db_session.exec(group_by_query).all()

            grouped_results = []
            for row in results:
                row_values = [row] if len(group_columns) == 1 else row
                keys_dict = {}
                one_record_query = query.with_only_columns(model)
                for i, col_val in enumerate(row_values):
                    one_record_query = one_record_query.where(group_columns[i] == col_val)
                    keys_dict[group_by[i]] = col_val

                grouped_results.append(
                    GroupResultType(keys=keys_dict, query_wrapper=QueryWrapper(
                        query=one_record_query, model=model
                        )
                    )
                )

            return grouped_results

        return {
            f"{model_name.lower()}s": strawberry.field(resolver=base_class_query),
            f"{model_name.lower()}s_grouped": strawberry.field(resolver=grouped_query)
        }

    def _create_model_types(self, model_name: str, model_class: typing.Type[SQLModel]):
        @strawberry.type(name=model_name)
        class EntityType(metaclass=BaseTypesMetaclass):
            model = model_class
        
        AggregateType = strawberry.type(
            AgregateTypeMetaclass(f"{model_name}Aggregate", (object,), {"model": model_class})
        )

        @strawberry.type(name=f"{model_name}GroupResult")
        class GroupResultType:
            _keys: strawberry.Private[dict]
            _query_wrapper: strawberry.Private[QueryWrapper]

            def __init__(self, keys: dict, query_wrapper: QueryWrapper):
                self._keys = keys
                self._query_wrapper = query_wrapper

            @strawberry.field
            def keys(self) -> typing.List[GroupKey]:
                return [GroupKey(name=k, value=str(v)) for k, v in self._keys.items()]

            @strawberry.field
            def nodes(self, info: strawberry.Info) -> typing.List[EntityType]:
                db_session = info.context['db_session']
                results = db_session.exec(self._query_wrapper.query).all()
                return results

            @strawberry.field
            def aggregate(self) -> AggregateType:
                return self._query_wrapper # type: ignore

        @strawberry.input(name=f"OrderBy{model_name}")
        class OrderByType(metaclass=BaseTypesMetaclass):
            model = model_class
            allowed_types = {int, str, float, bool}
            annotation_for_field_func = lambda *args, **kwargs: typing.Optional[OrderByDirection]

        return EntityType, GroupResultType, OrderByType
