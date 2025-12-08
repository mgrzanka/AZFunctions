from pydantic import BaseModel


class FileResponse(BaseModel):
    message: str
    file_content: str


class UpdateConfigReqest(BaseModel):
    new_config_file_content: str

class UpdateConfigResponse(BaseModel):
    status: str
