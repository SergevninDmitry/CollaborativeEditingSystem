from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from dependencies import get_access_token, get_clients
from clients.registry import Clients
from shared.common.schemas.version import (
    AddVersionRequest,
    DocumentVersionResponse,
)
from utils.http import build_response

import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Versions"])


@router.post(
    "/{document_id}/versions",
    response_model=DocumentVersionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new document version",
    description="Creates a new version based on the current document content.",
    responses={
        201: {"description": "Version successfully created"},
        409: {"description": "Version conflict detected"},
    },
)
async def add_version(
        document_id: UUID,
        data: AddVersionRequest,
        token: str = Depends(get_access_token),
        clients: Clients = Depends(get_clients),
):
    logger.info(f"[VERSION ADD] document={document_id}")

    r = await clients.versions.add_version(
        token,
        str(document_id),
        data.model_dump(),
    )

    if r.status_code not in (200, 201):
        raise HTTPException(r.status_code, r.json())

    return build_response(r)


@router.get(
    "/{document_id}/versions",
    response_model=list[DocumentVersionResponse],
    summary="Get document versions",
    description="Returns version history for a document.",
)
async def get_versions(
        document_id: UUID,
        token: str = Depends(get_access_token),
        clients: Clients = Depends(get_clients),
):
    logger.info(f"[VERSION LIST] document={document_id}")

    r = await clients.versions.get_versions(token, str(document_id))

    if r.status_code != status.HTTP_200_OK:
        raise HTTPException(r.status_code, r.json())

    return build_response(r)


@router.post(
    "/{document_id}/revert/{version_id}",
    response_model=DocumentVersionResponse,
    summary="Revert document",
    description="Creates a new version by reverting to a previous one.",
)
async def revert(
        document_id: UUID,
        version_id: UUID,
        token: str = Depends(get_access_token),
        clients: Clients = Depends(get_clients),
):
    logger.info(
        f"[VERSION REVERT] document={document_id} version={version_id}"
    )

    r = await clients.versions.revert(
        token,
        str(document_id),
        str(version_id),
    )

    if r.status_code != status.HTTP_200_OK:
        raise HTTPException(r.status_code, r.json())

    return build_response(r)


@router.get(
    "/{document_id}/diff/{version_id}",
    summary="Get version diff",
    description="Returns textual diff between selected version and previous version.",
)
async def diff(
        document_id: UUID,
        version_id: UUID,
        token: str = Depends(get_access_token),
        clients: Clients = Depends(get_clients),
):
    logger.info(
        f"[VERSION DIFF] document={document_id} version={version_id}"
    )

    r = await clients.versions.get_diff(
        token,
        str(document_id),
        str(version_id),
    )

    if r.status_code != status.HTTP_200_OK:
        raise HTTPException(r.status_code, r.json())

    return build_response(r)
