from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class DocumentVersionCreate(BaseModel):
    content: str


class DocumentVersionResponse(BaseModel):
    id: UUID
    document_id: UUID
    content: str
    created_by: UUID
    created_at: datetime
    author_email: str

    class Config:
        from_attributes = True


class AddVersionRequest(BaseModel):
    content: str
    base_version_id: UUID
