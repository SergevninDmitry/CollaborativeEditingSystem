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
    DocumentVersionResponse,
    AddVersionRequest
)
from dependencies import (
    get_current_user,
    get_user_service,
    get_version_service
)

import logging
import time

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Versions"])


@router.post("/{document_id}/versions")
async def add_version(
        document_id: UUID,
        data: AddVersionRequest,
        user_id: UUID = Depends(get_current_user),
        version_service: DocumentVersionService = Depends(get_version_service),
):
    try:
        version = await version_service.add_version(
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
        limit: int = 8,
        user_id: UUID = Depends(get_current_user),
        version_service: DocumentVersionService = Depends(get_version_service),
):
    return await version_service.get_versions(document_id)


@router.post("/{document_id}/revert/{version_id}", response_model=DocumentVersionResponse)
async def revert_version(
        document_id: UUID,
        version_id: UUID,
        user_id: UUID = Depends(get_current_user),
        version_service: DocumentVersionService = Depends(get_version_service),
        user_service: UserService = Depends(get_user_service),
):
    start_time = time.time()

    logger.info(
        f"[REVERT REQUEST] user={user_id} document={document_id} target_version={version_id}"
    )

    new_version = await version_service.revert_to_version(
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


@router.get("/{document_id}/diff/{version_id}")
async def get_diff(
        document_id: UUID,
        version_id: UUID,
        version_service: DocumentVersionService = Depends(get_version_service),
):
    return {
        "diff": await version_service.get_diff(
            document_id,
            version_id
        )
    }
