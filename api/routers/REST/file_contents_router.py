from fastapi import APIRouter, Depends

from api.schemas.file_contents_schemas import FileResponse
from api.dependencies import get_blob_service
from api.external_services.blob_storage_service import BlobService
from api.config.BlobHolderService import BlobHolderService
from api.config.envs import CONFIG_BLOB_NAME


blob_holder_service = BlobHolderService()

router = APIRouter(
    prefix="/files",
    tags=["Files"],
)

@router.get("/", response_model=FileResponse)
def get_config() -> FileResponse:
    config_content = blob_holder_service.get_blob_content(CONFIG_BLOB_NAME)
    
    print(f"Reading CONFIG: {config_content}")
    
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
