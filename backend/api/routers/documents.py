from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from services import (
    DocumentService,
    DocumentNotFound,
    UserService,
    DocumentVersionService
)
from db.schemas import (
    DocumentCreate,
    DocumentResponse,
    DocumentVersionResponse,
    AddVersionRequest,
    ShareRequest
)
from dependencies import (
    get_current_user,
    get_document_service,
    get_user_service,
    get_version_service
)
from db.models import User
from sqlalchemy import select

import logging
import time

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Documents"])


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
        data: DocumentCreate,
        user_id: UUID = Depends(get_current_user),
        service: DocumentService = Depends(get_document_service),
):
    document = await service.create_document(data, user_id)
    return document


@router.get("/", response_model=List[DocumentResponse])
async def get_documents(
        user_id: UUID = Depends(get_current_user),
        service: DocumentService = Depends(get_document_service),
):
    return await service.get_documents(user_id)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
        document_id: UUID,
        user_id: UUID = Depends(get_current_user),
        service: DocumentService = Depends(get_document_service),
):
    try:
        document = await service.get_document(document_id)

        if document.owner_id != user_id:
            raise HTTPException(status_code=403, detail="Forbidden")

        return document

    except DocumentNotFound:
        raise HTTPException(status_code=404, detail="Document not found")


@router.post("/{document_id}/share")
async def share_document(
        document_id: UUID,
        data: ShareRequest,
        user_id: UUID = Depends(get_current_user),
        document_service: DocumentService = Depends(get_document_service),
        user_service: UserService = Depends(get_user_service),
):
    target_user = await user_service.get_user_by_email(data.email)

    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    return await document_service.share_document(
        document_id,
        user_id,
        target_user.id
    )
