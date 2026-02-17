import logging

import httpx
from config import settings
from shared.common.schemas.user import UserAuthData

logger = logging.getLogger(__name__)


class HttpUserClient:

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=5.0)

    async def get_user_by_email(self, email: str) -> UserAuthData | None:
        response = await self.client.get(
            f"{settings.USER_SERVICE_URL}/users/internal/auth-data",
            params={"email": email},
            headers={
                "x-service-token": settings.INTERNAL_SERVICE_TOKEN
            }
        )
        logger.info(f"response: {response}")
        if response.status_code == 404:
            return None

        if response.status_code != 200:
            raise Exception(
                f"User service error: {response.status_code} {response.text}"
            )

        return UserAuthData.model_validate(response.json())

    async def close(self):
        await self.client.aclose()
