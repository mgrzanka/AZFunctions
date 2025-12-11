from typing import List
from sqlmodel import Field, SQLModel, Relationship
from api.models.purchase_model import Purchase, PurchasePublic


class UserBase(SQLModel):
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    purchases: List["Purchase"] = Relationship(back_populates="user")


class UserPublic(UserBase):
    id: int
    purchases: List[PurchasePublic] = []


class UserUpdate(UserBase):
    name: str | None = None # type: ignore
    age: int | None = None
