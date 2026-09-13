from uuid import UUID
from pydantic import BaseModel


class UploadSourceResponse(BaseModel):
    source_id: UUID
    job_id: UUID
    status: str
    filename: str