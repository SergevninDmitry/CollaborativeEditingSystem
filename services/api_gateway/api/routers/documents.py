from fastapi import APIRouter, Depends
from dependencies import get_access_token
from clients.http_document_client import DocumentClient
from shared.common.schemas.document import *
from utils.http import build_response

router = APIRouter(tags=["Documents"])
client = DocumentClient()


@router.post("/", response_model=DocumentResponse)
async def create_document(
    data: DocumentCreate,
    token: str = Depends(get_access_token),
):
    r = await client.create(token, data.model_dump())
    return build_response(r)

@router.get("/")
async def get_documents(token: str = Depends(get_access_token)):
    r = await client.list(token)
    return build_response(r)

@router.get("/{document_id}")
async def get_document(document_id: str,
                       token: str = Depends(get_access_token)):
    r = await client.get_document(token, document_id)
    return build_response(r)

@router.post("/{document_id}/share")
async def share_document(
    document_id: str,
    data: ShareRequest,
    token: str = Depends(get_access_token),
):
    r = await client.share(token, document_id, data.model_dump())
    return build_response(r)