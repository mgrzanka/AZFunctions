from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class UserPublic(UserBase):
    id: int


class UserUpdate(UserBase):
    name: str | None = None # type: ignore
    age: int | None = None
