from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime


class DocumentCreate(BaseModel):
    title: str
    content: str


class DocumentResponse(BaseModel):
    id: UUID
    title: str
    owner_id: UUID
    created_at: datetime


class ShareRequest(BaseModel):
    email: EmailStr
