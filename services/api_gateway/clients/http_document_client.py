import httpx
from config import settings

class DocumentClient:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=settings.DOCUMENT_SERVICE_URL)

    async def create(self, token: str, data: dict):
        response = await self.client.post("/documents/", json=data, headers={"Authorization": f"Bearer {token}"})
        return response

    async def get_documents(self, token: str):
        response = await self.client.get("/documents/", headers={"Authorization": f"Bearer {token}"})
        return response

    async def get_document(self, token: str, document_id: str):
        response = await self.client.get(f"/documents/{document_id}", headers={"Authorization": f"Bearer {token}"})
        return response

    async def share(self, token: str, document_id: str, data: dict):
        response = await self.client.post(f"/documents/{document_id}/share", json=data, headers={"Authorization": f"Bearer {token}"})
        return response
