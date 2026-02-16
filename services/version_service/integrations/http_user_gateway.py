import os
import httpx
from uuid import UUID

from domains.versions.contracts import VersionAuthor
from domains.versions.gateways.user_gateway import UserGateway
from config import settings

class HttpUserGateway(UserGateway):

    def __init__(self):
        self.api_url = settings.USER_SERVICE_URL
        self.client = httpx.AsyncClient(timeout=3.0)

    async def get_author(self, user_id: UUID) -> VersionAuthor:
        try:
            response = await self.client.get(
                f"{self.api_url}/users/{user_id}"
            )
            response.raise_for_status()

            data = response.json()

            return VersionAuthor(
                user_id=user_id,
                email=data["email"],
            )

        except (httpx.RequestError, httpx.HTTPStatusError):
            return VersionAuthor(
                user_id=user_id,
                email="unknown"
            )

    async def close(self):
        await self.client.aclose()
