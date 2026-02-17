from fastapi import APIRouter, Depends
from dependencies import get_access_token
from shared.common.schemas.document import *
from utils.http import build_response
from dependencies import get_clients
from clients.registry import Clients

router = APIRouter(tags=["Documents"])


@router.post("/", response_model=DocumentResponse)
async def create_document(
        data: DocumentCreate,
        clients: Clients = Depends(get_clients),
        token: str = Depends(get_access_token),
):
    r = await clients.documents.create(token, data.model_dump())
    return build_response(r)


@router.get("/")
async def get_documents(
        token: str = Depends(get_access_token),
        clients: Clients = Depends(get_clients),
):
    r = await clients.documents.get_documents(token)
    return build_response(r)


@router.get("/{document_id}")
async def get_document(
        document_id: str,
        token: str = Depends(get_access_token),
        clients: Clients = Depends(get_clients),
):
    r = await clients.documents.get_document(token, document_id)
    return build_response(r)


@router.post("/{document_id}/share")
async def share_document(
        document_id: str,
        data: ShareRequest,
        token: str = Depends(get_access_token),
        clients: Clients = Depends(get_clients),
):
    r = await clients.documents.share(token, document_id, data.model_dump())
    return build_response(r)
