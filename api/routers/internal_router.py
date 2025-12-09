from fastapi import APIRouter, Request, Depends, Body
import logging

from api.schemas.file_contents_schemas import UpdateConfigRequest, UpdateConfigResponse
from api.dependencies import validate_internal_secret


router = APIRouter(
    prefix="/_internal",
    tags=["internal"],
    dependencies=[Depends(validate_internal_secret)]
)

@router.post("/config_update", response_model=UpdateConfigResponse)
async def update_config_webhook(request: Request, new_config: UpdateConfigRequest = Body(...)):
    logging.info(f"Received POST request to /_internal/config_update with method: {request.method}, path: {request.url.path}")
    try:
        if new_config.new_config_file_content:
            setattr(request.app.state, "config_file_data", new_config.new_config_file_content)
            logging.info(f"Current state: {request.app.state.__dict__}")
            logging.info("Config file updated successfully")
            return UpdateConfigResponse(status="Config Updated")

        logging.warning("No config file content provided")
        return UpdateConfigResponse(status="Error while updating config file")

    except Exception as e:
        logging.error(f"Error while updating config file: {e}", exc_info=True)
        return UpdateConfigResponse(status="Error while updating config file")
