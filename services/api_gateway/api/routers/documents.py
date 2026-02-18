from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List

from dependencies import get_access_token, get_clients
from clients.registry import Clients
from shared.common.schemas.document import (
    DocumentCreate,
    DocumentResponse,
    ShareRequest,
)
from utils.http import build_response

import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Documents"])


@router.post(
    "/",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create document",
    description="""
Creates a new collaborative document.

The authenticated user becomes the document owner.
The initial version is created automatically.
""",
    responses={
        201: {"description": "Document successfully created"},
        401: {"description": "Unauthorized"},
        500: {"description": "Document service error"},
    },
)
async def create_document(
        data: DocumentCreate,
        token: str = Depends(get_access_token),
        clients: Clients = Depends(get_clients),
):
    logger.info("[DOCUMENT CREATE]")

    r = await clients.documents.create(token, data.model_dump(mode="json"))

    if r.status_code != status.HTTP_201_CREATED:
        raise HTTPException(r.status_code, r.json())

    return build_response(r)


@router.get(
    "/",
    response_model=List[DocumentResponse],
    summary="Get user documents",
    description="""
Returns all documents доступные пользователю:

- owned documents
- shared documents
""",
    responses={
        200: {"description": "List of documents"},
        401: {"description": "Unauthorized"},
    },
)
async def get_documents(
        token: str = Depends(get_access_token),
        clients: Clients = Depends(get_clients),
):
    logger.info("[DOCUMENT LIST]")

    r = await clients.documents.get_documents(token)

    if r.status_code != status.HTTP_200_OK:
        raise HTTPException(r.status_code, r.json())

    return build_response(r)


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Get document",
    description="Returns document metadata by ID.",
    responses={
        200: {"description": "Document found"},
        403: {"description": "Access forbidden"},
        404: {"description": "Document not found"},
    },
)
async def get_document(
        document_id: UUID,
        token: str = Depends(get_access_token),
        clients: Clients = Depends(get_clients),
):
    logger.info(f"[DOCUMENT GET] id={document_id}")

    r = await clients.documents.get_document(token, str(document_id))

    if r.status_code != status.HTTP_200_OK:
        raise HTTPException(r.status_code, r.json())

    return build_response(r)


@router.post(
    "/{document_id}/share",
    status_code=status.HTTP_200_OK,
    summary="Share document",
    description="""
Shares document with another user by email.
""",
    responses={
        200: {"description": "Document shared"},
        403: {"description": "Only owner can share"},
        404: {"description": "User or document not found"},
    },
)
async def share_document(
        document_id: UUID,
        data: ShareRequest,
        token: str = Depends(get_access_token),
        clients: Clients = Depends(get_clients),
):
    logger.info(f"[DOCUMENT SHARE] id={document_id} email={data.email}")

    r = await clients.documents.share(
        token,
        str(document_id),
        data.model_dump(mode="json"),
    )

    if r.status_code >= 400:
        raise HTTPException(
            status_code=r.status_code,
            detail=r.json().get("detail", "Service error"),
        )

    return build_response(r)
