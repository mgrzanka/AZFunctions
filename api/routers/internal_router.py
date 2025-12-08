from fastapi import APIRouter, Request, Depends
import logging

from api.schemas.file_contents_schemas import UpdateConfigReqest, UpdateConfigResponse
from api.dependencies import validate_internal_secret


router = APIRouter(
    prefix="/_internal",
    tags=["internal"],
    dependencies=[Depends(validate_internal_secret)]
)

@router.post("/config_update", response_model=UpdateConfigResponse)
def update_config_webhook(request: Request, new_config: UpdateConfigReqest):
    try:
        if new_config.new_config_file_content:
            setattr(request.app.state, "config_file_data", new_config.new_config_file_content)
            return UpdateConfigResponse(status="Config Updated")

        return UpdateConfigResponse(status="Error while updating config file")
    
    except Exception as e:
        logging.error(f"Error while updateing config file", e)
        return UpdateConfigResponse(status="Error while updating config file")
