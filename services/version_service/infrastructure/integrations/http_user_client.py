import httpx
from uuid import UUID
from config import settings


class HttpUserClient:

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=3.0)

    async def get_user_email(self, user_id: UUID) -> str:
        r = await self.client.get(
            f"{settings.USER_SERVICE_URL}/users/{user_id}"
        )

        if r.status_code != 200:
            return "unknown"

        return r.json()["email"]

    async def close(self):
        await self.client.aclose()
