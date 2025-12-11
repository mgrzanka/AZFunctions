import strawberry
import typing
from sqlmodel import Session, select, func, col

from api.routers.GraphQL.types import Item, Purchase, User, GeneralStatistics
from api.models.user_model import User as UserModel
from api.models.purchase_model import Purchase as PurchaseModel
from api.models.item_model import Item as ItemModel


@strawberry.type
class Query:
    general_statistics: GeneralStatistics = strawberry.field(resolver=GeneralStatistics)

    @strawberry.field
    def users(self,
              info: strawberry.Info,
              top_k_spending:  typing.Optional[int] = None,
              spending_over: typing.Optional[int] = None,
              offset: typing.Optional[int] = None,
              limit: typing.Optional[int] = None
        ) -> typing.List[User]:
        db_session: Session = info.context['db_session']

        query = select(UserModel)
        if spending_over or top_k_spending:
            query = query.join(PurchaseModel).join(ItemModel).group_by(col(UserModel.id))  
        if spending_over:
            query = query.having(func.sum(ItemModel.price) > spending_over)
        if top_k_spending:
            query = query.order_by(func.sum(ItemModel.price).desc())
            limit = top_k_spending

        query = query.offset(offset).limit(limit)

        users = db_session.exec(query).all()

        return [
            User(
                id=user.id or 0,
                name=user.name,
                age=user.age
            )
            for user in users
        ]

    @strawberry.field
    def items(self,
              info: strawberry.Info,
              offset: typing.Optional[int] = None,
              limit: typing.Optional[int] = None
    ) -> list[Item]:
        db_session: Session = info.context['db_session']
        query = select(ItemModel).offset(offset).limit(limit)
        items = db_session.exec(query).all()
        return [
            Item(
                id=item.id or 0,
                name=item.name,
                price=item.price,
                expiration_date=item.expiration_date
            )
            for item in items
        ]
