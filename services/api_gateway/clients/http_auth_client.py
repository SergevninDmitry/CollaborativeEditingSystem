import httpx
from config import settings
import logging

logger = logging.getLogger(__name__)


class AuthClient:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=settings.AUTH_SERVICE_URL)

    async def login(self, credentials: dict):
        response = await self.client.post("/auth/login", json=credentials)
        logger.info(f"AuthClient login r={response}")
        return response

    async def close(self):
        await self.client.aclose()
