from sqlmodel import create_engine, SQLModel, Session
from typing import Generator

from api.config.envs import DATABASE_CONNECTION_STRING
from api.models import User, Item, Purchase


engine = create_engine(DATABASE_CONNECTION_STRING)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
