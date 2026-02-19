from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional


class DocumentVersionCreate(BaseModel):
    content: str


class DocumentVersionResponse(BaseModel):
    id: UUID
    document_id: UUID
    content: str
    created_by: UUID
    created_at: datetime
    author_email: Optional[str] = None

    class Config:
        from_attributes = True


class AddVersionRequest(BaseModel):
    content: str
    base_version_id: Optional[UUID] = None
