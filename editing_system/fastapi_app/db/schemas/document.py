from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class DocumentCreate(BaseModel):
    title: str
    content: str


class DocumentResponse(BaseModel):
    id: UUID
    title: str
    owner_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class AddVersionRequest(BaseModel):
    content: str
    base_version_id: UUID
