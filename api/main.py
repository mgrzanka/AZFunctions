import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from api.routers import file_contents_router, internal_router
from api.external_services.blob_storage_service import BlobService
from api.env import STORAGE_ACCOUNT_URI, CLIENT_ID, STORAGE_CONTAINER_NAME, CONFIG_BLOB_NAME


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    blob_service = BlobService(STORAGE_ACCOUNT_URI, STORAGE_CONTAINER_NAME, CLIENT_ID)
    app.state.blob_service = blob_service
    app.state.config_file_data = blob_service.download_blob(CONFIG_BLOB_NAME).decode("utf-8")
    yield
    blob_service.close()


app = FastAPI(lifespan=lifespan)
app.include_router(file_contents_router.router)
app.include_router(internal_router.router)


@app.exception_handler(Exception)
async def validation_exception_handler(request: Request, exc: Exception):
    print(f"Error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": f"Something went wrong", "exception": str(exc)},
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
