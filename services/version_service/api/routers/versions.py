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

from dependencies import (
    get_version_service,
    get_current_user,
)

import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Versions"])


@router.post(
    "/{document_id}/versions",
    response_model=DocumentVersionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new document version",
    description="""
Creates a new version of a document.

If `base_version_id` is provided, optimistic locking is applied.
Request fails if the document was modified by another user.
""",
    responses={
        201: {"description": "Version successfully created"},
        409: {"description": "Version conflict (document changed)"},
        401: {"description": "Unauthorized"},
    },
)
async def add_version(
        document_id: UUID,
        data: AddVersionRequest,
        user_id: UUID = Depends(get_current_user),
        service: DocumentVersionService = Depends(get_version_service),
):
    """
    Adds a new version of a document.
    """
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


@router.get(
    "/{document_id}/versions",
    response_model=list[DocumentVersionResponse],
    summary="Get document versions",
    description="Returns latest versions of a document ordered by creation time.",
)
async def get_versions(
        document_id: UUID,
        service: DocumentVersionService = Depends(get_version_service),
):
    """
    Retrieve version history for a document.
    """
    return await service.get_versions(document_id)


@router.post(
    "/{document_id}/revert/{version_id}",
    response_model=DocumentVersionResponse,
    summary="Revert document to a previous version",
    description="""
Creates a new version using content from a selected historical version.

The original version remains unchanged.
""",
    responses={
        200: {"description": "Document successfully reverted"},
        404: {"description": "Version not found"},
        401: {"description": "Unauthorized"},
    },
)
async def revert_version(
        document_id: UUID,
        version_id: UUID,
        user_id: UUID = Depends(get_current_user),
        service: DocumentVersionService = Depends(get_version_service),
):
    """
    Reverts document content to a selected version.
    """
    try:
        return await service.revert_to_version(
            document_id,
            version_id,
            user_id,
        )

    except DocumentNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found",
        )


@router.get(
    "/{document_id}/diff/{version_id}",
    summary="Get diff between versions",
    description="""
Returns unified diff between selected version and its previous version.
Useful for displaying document changes.
""",
    responses={
        200: {"description": "Diff generated successfully"},
        404: {"description": "Version not found"},
    },
)
async def get_diff(
        document_id: UUID,
        version_id: UUID,
        service: DocumentVersionService = Depends(get_version_service),
):
    """
    Returns textual diff between document versions.
    """
    return {
        "diff": await service.get_diff(document_id, version_id)
    }
