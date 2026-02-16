import httpx
from config import settings

class VersionClient:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=settings.VERSION_SERVICE_URL)

    async def add_version(self, token: str, document_id: str, data: dict):
        response = await self.client.post(f"/versions/{document_id}/versions", json=data, headers={"Authorization": f"Bearer {token}"})
        return response

    async def get_versions(self, token: str, document_id: str):
        response = await self.client.get(f"/versions/{document_id}/versions", headers={"Authorization": f"Bearer {token}"})
        return response

    async def revert(self, token: str, document_id: str, version_id: str):
        response = await self.client.post(f"/versions/{document_id}/revert/{version_id}", headers={"Authorization": f"Bearer {token}"})
        return response

    async def get_diff(self, token: str, document_id: str, version_id: str):
        response = await self.client.get(f"/versions/{document_id}/diff/{version_id}", headers={"Authorization": f"Bearer {token}"})
        return response
