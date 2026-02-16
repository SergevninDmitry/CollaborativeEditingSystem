import httpx
from config import settings


class AuthClient:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=settings.AUTH_SERVICE_URL)

    async def login(self, credentials: dict):
        response = await self.client.post("/auth/login", json=credentials)
        return response
