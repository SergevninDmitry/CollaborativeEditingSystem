from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from editing_system.fastapi_app.services import (
    DocumentService,
    DocumentNotFound,
    UserService
)
from editing_system.fastapi_app.db.schemas import (
    DocumentCreate,
    DocumentResponse,
    DocumentVersionCreate,
    DocumentVersionResponse,
    AddVersionRequest,
    ShareRequest
)
from editing_system.fastapi_app.dependencies import (
    get_current_user,
    get_document_service,
    get_user_service
)
from editing_system.fastapi_app.db.models import User
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


@router.post("/{document_id}/versions")
async def add_version(
        document_id: UUID,
        data: AddVersionRequest,
        user_id: UUID = Depends(get_current_user),
        service: DocumentService = Depends(get_document_service),
):
    try:
        version = await service.add_version(
            document_id,
            data.content,
            user_id,
            data.base_version_id,
        )
        logger.info(
            f"[add_version SUCCESS] user={user_id} document={document_id} "
            f"content={data.content} base_version_id={data.base_version_id}"
        )

        return version
    except Exception as e:
        logger.error(
            f"[add_version FAILED] user={user_id} document={document_id} "
            f"content={data.content} base_version_id={data.base_version_id}"
            f"error:{e}"
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document was modified by another user",
        )


@router.get("/{document_id}/versions", response_model=List[DocumentVersionResponse])
async def get_versions(
        document_id: UUID,
        user_id: UUID = Depends(get_current_user),
        service: DocumentService = Depends(get_document_service),
):
    return await service.get_versions(document_id)


@router.post("/{document_id}/revert/{version_id}", response_model=DocumentVersionResponse)
async def revert_version(
        document_id: UUID,
        version_id: UUID,
        user_id: UUID = Depends(get_current_user),
        document_service: DocumentService = Depends(get_document_service),
        user_service: UserService = Depends(get_user_service),
):
    start_time = time.time()

    logger.info(
        f"[REVERT REQUEST] user={user_id} document={document_id} target_version={version_id}"
    )

    new_version = await document_service.revert_to_version(
        document_id,
        version_id,
        user_id,
    )

    # получаем email пользователя
    user_obj = await user_service.get_user(user_id)
    author_email = user_obj.email if user_obj else "unknown"

    duration = round(time.time() - start_time, 4)

    logger.info(
        f"[REVERT SUCCESS] user={user_id} author_email= {author_email} document={document_id} "
        f"new_version={new_version.id} duration={duration}s"
    )

    return {
        "id": new_version.id,
        "document_id": new_version.document_id,
        "content": new_version.content,
        "created_by": new_version.created_by,
        "created_at": new_version.created_at,
        "author_email": author_email
    }


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
