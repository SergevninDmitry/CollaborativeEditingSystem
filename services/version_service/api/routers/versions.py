from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from application.versions.version_service import (
    DocumentVersionService,
    DocumentNotFound,
    VersionConflict,
)
from infrastructure.db.schemas.version import (
    DocumentVersionResponse,
    AddVersionRequest,
)

from dependencies import get_version_service, get_current_user

import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Versions"])


@router.post("/{document_id}/versions")
async def add_version(
    document_id: UUID,
    data: AddVersionRequest,
    user_id: UUID = Depends(get_current_user),
    service: DocumentVersionService = Depends(get_version_service),
):
    try:
        version = await service.add_version(
            document_id,
            data.content,
            user_id,
            data.base_version_id,
        )

        logger.info(
            f"[add_version SUCCESS] user={user_id} document={document_id}"
        )

        return version

    except VersionConflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document was modified by another user",
        )


@router.get("/{document_id}/versions")
async def get_versions(
    document_id: UUID,
    service: DocumentVersionService = Depends(get_version_service),
):
    return await service.get_versions(document_id)


@router.post(
    "/{document_id}/revert/{version_id}",
    response_model=DocumentVersionResponse,
)
async def revert_version(
    document_id: UUID,
    version_id: UUID,
    user_id: UUID = Depends(get_current_user),
    service: DocumentVersionService = Depends(get_version_service),
):
    try:
        return await service.revert_to_version(
            document_id,
            version_id,
            user_id,
        )
    except DocumentNotFound:
        raise HTTPException(404, "Version not found")


@router.get("/{document_id}/diff/{version_id}")
async def get_diff(
    document_id: UUID,
    version_id: UUID,
    service: DocumentVersionService = Depends(get_version_service),
):
    return {
        "diff": await service.get_diff(document_id, version_id)
    }
