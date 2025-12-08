from fastapi import APIRouter, Request, Depends

from api.schemas.file_contents_schemas import FileResponse
from api.dependencies import get_blob_service
from api.external_services.blob_storage_service import BlobService


router = APIRouter(
    prefix="/files",
    tags=["files"],
)

@router.get("/", response_model=FileResponse)
def get_config(request: Request) -> FileResponse:
    config_content = getattr(request.app.state, "config_file_data", "Config not loaded")
    return FileResponse(
        message="Hello World!",
        file_content=config_content
    )


@router.get("/{filename}", response_model=FileResponse)
def download(filename: str, service: BlobService = Depends(get_blob_service)):
    file_content = service.download_blob(filename).decode("utf-8")
    return FileResponse(
        message=f"This is {filename} file",
        file_content=file_content
    )
