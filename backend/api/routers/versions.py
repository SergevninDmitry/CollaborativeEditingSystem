from fastapi import APIRouter, Depends
from uuid import UUID
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import httpx
import os

router = APIRouter(tags=["Versions"])

security = HTTPBearer()

VERSION_SERVICE_URL = os.getenv(
    "VERSION_SERVICE_URL",
    "http://version_service:8001"
)


@router.get("/{document_id}/versions")
async def get_versions(
        document_id: UUID,
        limit: int = 8,
        credentials: HTTPAuthorizationCredentials = Depends(security),
):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{VERSION_SERVICE_URL}/versions/{document_id}/versions",
            params={"limit": limit},
            headers={
                "Authorization": f"Bearer {credentials.credentials}"
            }
        )

    response.raise_for_status()
    return response.json()


@router.post("/{document_id}/revert/{version_id}")
async def revert_version(
        document_id: UUID,
        version_id: UUID,
        credentials: HTTPAuthorizationCredentials = Depends(security),
):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{VERSION_SERVICE_URL}/versions/{document_id}/revert/{version_id}",
            headers={
                "Authorization": f"Bearer {credentials.credentials}"
            }
        )

    response.raise_for_status()
    return response.json()


@router.get("/{document_id}/diff/{version_id}")
async def get_diff(
        document_id: UUID,
        version_id: UUID,
        credentials: HTTPAuthorizationCredentials = Depends(security),
):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{VERSION_SERVICE_URL}/versions/{document_id}/diff/{version_id}",
            headers={
                "Authorization": f"Bearer {credentials.credentials}"
            }
        )

    response.raise_for_status()
    return response.json()


@router.post("/{document_id}/versions")
async def add_version(
    document_id: UUID,
    data: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{VERSION_SERVICE_URL}/versions/{document_id}/versions",
            json=data,
            headers={
                "Authorization": f"Bearer {credentials.credentials}"
            }
        )

    response.raise_for_status()
    return response.json()
