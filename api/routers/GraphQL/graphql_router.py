import strawberry
from fastapi import Depends

from api.database import get_session
from api.routers.GraphQL.queries import Query
from api.routers.GraphQL.mutations import Mutation


async def get_context(db_session=Depends(get_session)):
    return {
        "db_session": db_session
    }

schema = strawberry.Schema(query=Query, mutation=Mutation)
