import httpx
from config import settings


class HttpUserClient:

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=5.0)

    async def get_user_by_email(self, email: str):
        response = await self.client.get(
            f"{settings.USER_SERVICE_URL}/users/internal/auth-data",
            params={"email": email}
        )

        if response.status_code == 404:
            return None

        return response.json()

    async def close(self):
        await self.client.aclose()
