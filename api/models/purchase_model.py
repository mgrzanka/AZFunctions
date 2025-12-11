from typing import TYPE_CHECKING
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from api.models.item_model import Item
    from api.models.user_model import User


class PurchaseBase(SQLModel):
    user_id: int = Field(foreign_key="user.id")
    item_id: int = Field(foreign_key="item.id")


class Purchase(PurchaseBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user: "User" = Relationship(back_populates="purchases")
    item: "Item" = Relationship(back_populates="purchases")


class PurchasePublic(PurchaseBase):
    id: int
