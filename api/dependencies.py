from api.external_services.blob_storage_service import BlobService
from fastapi import Request


def get_blob_service(request: Request) -> BlobService:
    return request.app.state.blob_service
