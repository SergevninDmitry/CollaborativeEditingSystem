from fastapi import APIRouter, Depends
from dependencies import get_access_token
from clients.http_version_client import VersionClient
from utils.http import build_response


router = APIRouter(tags=["Versions"])
client = VersionClient()


@router.post("/{document_id}/versions")
async def add_version(document_id: str,
                      data: dict,
                      token: str = Depends(get_access_token)):
    r = await client.add_version(token, document_id, data)
    return build_response(r)


@router.get("/{document_id}/versions")
async def get_versions(document_id: str,
                       token: str = Depends(get_access_token)):
    r = await client.get_versions(token, document_id)
    return build_response(r)


@router.post("/{document_id}/revert/{version_id}")
async def revert(document_id: str,
                 version_id: str,
                 token: str = Depends(get_access_token)):
    r = await client.revert(token, document_id, version_id)
    return build_response(r)


@router.get("/{document_id}/diff/{version_id}")
async def diff(document_id: str,
               version_id: str,
               token: str = Depends(get_access_token)):
    r = await client.diff(token, document_id, version_id)
    return build_response(r)
