from pydantic import BaseModel


class FileResponse(BaseModel):
    message: str
    file_content: str
