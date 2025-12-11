import typing
import strawberry
from datetime import datetime
from sqlmodel import select, Session, col, func, distinct

from api.models.purchase_model import Purchase as PurchaseModel
from api.models.user_model import User as UserModel
from api.models.item_model import Item as ItemModel


@strawberry.type
class Purchase:
    id: int
    user: "User"
    item: "Item"


@strawberry.type
class ItemStatistics:
    _item_id: strawberry.Private[int]

    def __init__(self, item_id: int):
        self._item_id = item_id

    @strawberry.field
    def all_buyings_total_price(self, info: strawberry.Info) -> float:
        db_session: Session = info.context['db_session']
        query = (
            select(func.sum(ItemModel.price)).
            join(PurchaseModel).
            where(PurchaseModel.item_id == self._item_id)
        )
        total_spend = db_session.exec(query).one_or_none()
        return float(total_spend) if total_spend else 0.0

    @strawberry.field
    def num_purchases(self, info: strawberry.Info) -> int:
        db_session: Session = info.context['db_session']
        query = (
            select(func.count(col(PurchaseModel.id))).
            where(PurchaseModel.item_id == self._item_id)
        )
        num_purchases = db_session.exec(query).one_or_none()
        return int(num_purchases) if num_purchases else 0


@strawberry.type
class Item:
    id: int
    name: str
    price: float
    expiration_date: datetime | None

    @strawberry.field
    def statistics(self) -> ItemStatistics:
        return ItemStatistics(item_id=self.id)


@strawberry.type
class UserStatistics:
    _user_id: strawberry.Private[int]

    def __init__(self, user_id: int):
        self._user_id = user_id

    @strawberry.field
    def top_expensive_purchase(self, info: strawberry.Info) -> typing.Optional[Purchase]:
        db_session: Session = info.context['db_session']
        query = (
            select(PurchaseModel).
            join(ItemModel).
            where(PurchaseModel.user_id == self._user_id).
            order_by(col(ItemModel.price))
            .limit(1)
        )
        purchase = db_session.exec(query).first()
        if not purchase:
            return None
        item = db_session.exec(select(ItemModel).where(ItemModel.id == purchase.item_id)).one()
        user = db_session.exec(select(UserModel).where(UserModel.id == purchase.user_id)).one()

        return Purchase(
            id=purchase.id or 0,
            user=User(id=user.id or 0, name=user.name, age=user.age),
            item=Item(
                id=item.id or 0,
                name=item.name,
                price=item.price,
                expiration_date=item.expiration_date
            )
        )

    @strawberry.field
    def num_purchases(self, info: strawberry.Info) -> int:
        db_session: Session = info.context['db_session']
        query = (
            select(func.count(col(PurchaseModel.id))).
            where(PurchaseModel.user_id == self._user_id)
        )
        num_purchases = db_session.exec(query).one_or_none()
        return int(num_purchases) if num_purchases else 0

    @strawberry.field
    def total_spent(self, info: strawberry.Info) -> float:
        db_session: Session = info.context['db_session']
        query = (
            select(func.sum(ItemModel.price)).
            join(PurchaseModel).
            where(PurchaseModel.user_id == self._user_id)
        )
        total_spend = db_session.exec(query).one_or_none()
        return float(total_spend) if total_spend else 0.0


@strawberry.type
class User:
    id: int
    name: str
    age: int | None

    @strawberry.field
    def purchases(self, info: strawberry.Info) -> typing.List[Purchase]:
        db_session: Session = info.context['db_session']

        query = select(PurchaseModel).where(PurchaseModel.user_id == self.id)
        results: list[PurchaseModel] = list(db_session.exec(query).all())

        return [
            Purchase(
                id=purchase.id or 0,
                user=self,
                item=Item(
                    id=purchase.item.id or 0,
                    name=purchase.item.name,
                    price=purchase.item.price,
                    expiration_date=purchase.item.expiration_date
                )
            )
            for purchase in results
        ]

    @strawberry.field
    def statistics(self) -> UserStatistics:
        return UserStatistics(user_id=self.id)


@strawberry.type
class GeneralStatistics:
    @strawberry.field
    def avg_user_spending(self,  info: strawberry.Info) -> float:
        db_session: Session = info.context['db_session']
        revenue_query = (
            select(func.sum(ItemModel.price)).
            join(PurchaseModel)
        )
        total_revenue = db_session.exec(revenue_query).one_or_none() or 0.0

        users_query = select(func.count(distinct(PurchaseModel.user_id)))
        total_users = db_session.exec(users_query).one_or_none() or 0
        if total_users == 0:
            return 0.0

        return float(total_revenue) / float(total_users)

    @strawberry.field
    def total_money_earned(self,  info: strawberry.Info) -> float:
        db_session: Session = info.context['db_session']

        query = (
            select(func.sum(ItemModel.price)).
            join(PurchaseModel)
        )
        total_earned = db_session.exec(query).one_or_none()
        return float(total_earned) if total_earned else 0.0
