from api.external_services.blob_storage_service import BlobService
from fastapi import Request, Security, HTTPException
from fastapi.security import APIKeyHeader
import secrets

from api.config.envs import INTERNAL_SECRET


def validate_internal_secret(api_key: str = Security(APIKeyHeader(name="X-Internal-Secret"))):
    if not secrets.compare_digest(INTERNAL_SECRET, api_key):
        raise HTTPException(401)


def get_blob_service(request: Request) -> BlobService:
    return request.app.state.blob_service
