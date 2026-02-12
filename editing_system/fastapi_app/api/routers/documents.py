from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from editing_system.fastapi_app.services import (
    DocumentService,
    DocumentNotFound,
)
from editing_system.fastapi_app.db.schemas import (
    DocumentCreate,
    DocumentResponse,
    DocumentVersionCreate,
    DocumentVersionResponse,
    AddVersionRequest
)
from editing_system.fastapi_app.dependencies import (
    get_current_user,
    get_document_service
)
import logging


router = APIRouter(tags=["Documents"])


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
        data: DocumentCreate,
        user_id: str = Depends(get_current_user),
        service: DocumentService = Depends(get_document_service),
):
    document = await service.create_document(data, user_id)
    return document


@router.get("/", response_model=List[DocumentResponse])
async def get_documents(
        user_id: str = Depends(get_current_user),
        service: DocumentService = Depends(get_document_service),
):
    return await service.get_documents(user_id)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
        document_id: UUID,
        user_id: str = Depends(get_current_user),
        service: DocumentService = Depends(get_document_service),
):
    try:
        document = await service.get_document(str(document_id))

        if document.owner_id != user_id:
            raise HTTPException(status_code=403, detail="Forbidden")

        return document

    except DocumentNotFound:
        raise HTTPException(status_code=404, detail="Document not found")


@router.post("/{document_id}/versions")
async def add_version(
        document_id: UUID,
        data: AddVersionRequest,
        user_id: str = Depends(get_current_user),
        service: DocumentService = Depends(get_document_service),
):
    try:
        version = await service.add_version(
            str(document_id),
            data.content,
            user_id,
            data.base_version_id,
        )
        return version
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document was modified by another user",
        )



@router.get("/{document_id}/versions", response_model=List[DocumentVersionResponse])
async def get_versions(
        document_id: UUID,
        user_id: str = Depends(get_current_user),
        service: DocumentService = Depends(get_document_service),
):
    return await service.get_versions(str(document_id))


@router.post("/{document_id}/revert/{version_id}", response_model=DocumentVersionResponse)
async def revert_version(
        document_id: UUID,
        version_id: UUID,
        user_id: str = Depends(get_current_user),
        service: DocumentService = Depends(get_document_service),
):
    return await service.revert_to_version(
        str(document_id),
        str(version_id),
        user_id,
    )
