import httpx
from uuid import UUID
from config import settings


class HttpUserClient:

    def __init__(self, client: httpx.AsyncClient | None = None):
        self.client = client or httpx.AsyncClient(timeout=3.0)

    async def get_user_email(self, user_id: UUID) -> str:
        r = await self.client.get(
            f"{settings.USER_SERVICE_URL}/users/{user_id}"
        )

        if r.status_code != 200:
            return "unknown"

        return r.json()["email"]

    async def get_users_batch(self, user_ids: list[UUID]) -> dict[UUID, str]:

        if not user_ids:
            return {}

        params = [("ids", str(uid)) for uid in user_ids]

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.USER_SERVICE_URL}/users/internal/batch",
                params=params,
                headers={
                    "x-service-token": settings.INTERNAL_SERVICE_TOKEN
                },
            )

            response.raise_for_status()

            data = response.json()

        # response format:
        # {
        #   "uuid": {"id": "...", "email": "..."}
        # }

        return {
            UUID(uid): user_data["email"]
            for uid, user_data in data.items()
        }

    async def close(self):
        await self.client.aclose()
