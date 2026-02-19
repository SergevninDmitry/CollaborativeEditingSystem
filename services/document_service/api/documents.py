from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from application.services.document_service import (
    DocumentService,
    DocumentNotFound,
)

from shared.common.schemas.document import (
    DocumentCreate,
    DocumentResponse,
    ShareRequest,
)

from dependencies import (
    get_current_user,
    get_document_service,
    get_access_token,
    get_user_client,
)

import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Documents"])


@router.post(
    "/",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new document",
    description="""
Creates a new document owned by the authenticated user.

An initial document version is automatically created
via Version Service.
""",
    responses={
        201: {"description": "Document successfully created"},
        401: {"description": "Unauthorized"},
        500: {"description": "Failed to create document version"},
    },
)
async def create_document(
    data: DocumentCreate,
    user_id: UUID = Depends(get_current_user),
    token: str = Depends(get_access_token),
    service: DocumentService = Depends(get_document_service),
):
    """
    Create a document and initialize its first version.
    """
    document = await service.create_document(data, user_id, token)
    return document


@router.get(
    "/",
    response_model=List[DocumentResponse],
    summary="Get user documents",
    description="""
Returns all documents available to the current user.

Includes:
- documents owned by the user
- documents shared with the user
""",
    responses={
        200: {"description": "List of accessible documents"},
        401: {"description": "Unauthorized"},
    },
)
async def get_documents(
    user_id: UUID = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    """
    Retrieve all documents accessible by the current user.
    """
    return await service.get_documents(user_id)



@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Get document by ID",
    description="""
Returns a single document if the authenticated user
is the owner of the document.
""",
    responses={
        200: {"description": "Document retrieved successfully"},
        403: {"description": "User is not allowed to access this document"},
        404: {"description": "Document not found"},
    },
)
async def get_document(
    document_id: UUID,
    user_id: UUID = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    """
    Retrieve document details by ID.
    """
    try:
        document = await service.get_document(document_id)

        if document.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden",
            )

        return document

    except DocumentNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

@router.post(
    "/{document_id}/share",
    summary="Share document with another user",
    description="""
Grants access to a document for another user using their email.

Only document owner can share the document.
""",
    responses={
        200: {"description": "Document shared successfully"},
        403: {"description": "Only owner can share document"},
        404: {"description": "Target user not found"},
    },
)
async def share_document(
    document_id: UUID,
    data: ShareRequest,
    user_id: UUID = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
    user_client=Depends(get_user_client),
):
    """
    Share document with another user by email.
    """

    target_user = await user_client.get_user_by_email(data.email)

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return await document_service.share_document(
        document_id,
        user_id,
        UUID(target_user["id"]),
    )

