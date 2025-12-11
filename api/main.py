import uvicorn
from fastapi import FastAPI, Request
from strawberry.fastapi import GraphQLRouter
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from api.routers.REST import file_contents_router, users_router
from api.routers.GraphQL import graphql_router
from api.external_services.blob_storage_service import create_blob_service
from api.database import create_db_and_tables
from api.config.envs import CONFIG_BLOB_NAME, QUERY_BLOB_NAME
from api.config.BlobHolderService import BlobHolderService


blob_holder_service = BlobHolderService()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    blob_service = create_blob_service()
    app.state.blob_service = blob_service

    config_file_data = blob_service.download_blob(CONFIG_BLOB_NAME).decode("utf-8")
    custom_query = blob_service.download_blob(QUERY_BLOB_NAME).decode("utf-8")
    blob_holder_service.update_blob_content(CONFIG_BLOB_NAME, config_file_data)
    blob_holder_service.update_blob_content(QUERY_BLOB_NAME, custom_query)

    create_db_and_tables()
    yield
    blob_service.close()


app = FastAPI(lifespan=lifespan)
app.include_router(file_contents_router.router)
app.include_router(users_router.router)
app.include_router(
    GraphQLRouter(graphql_router.schema, context_getter=graphql_router.get_context),
    prefix="/graphql"
)


@app.exception_handler(Exception)
async def validation_exception_handler(request: Request, exc: Exception):
    print(f"Error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": f"Something went wrong", "exception": str(exc)},
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
