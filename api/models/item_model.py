from typing import TYPE_CHECKING, List, Optional
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from api.models.purchase_model import Purchase


class ItemBase(SQLModel):
    name: str = Field(index=True)
    price: float = Field(default=0.0)
    expiration_date: datetime | None = Field(default_factory=datetime.now)


class Item(ItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    purchases: List["Purchase"] = Relationship(back_populates="item")
