import os
import httpx
from uuid import UUID

from domains.versions.contracts import VersionAuthor
from domains.versions.gateways.user_gateway import UserGateway


class HttpUserGateway(UserGateway):
    """
    Simulates remote microservice call.
    Later this becomes real user-service URL.
    """

    def __init__(self):
        self.api_url = os.getenv(
            "USER_SERVICE_URL",
            "http://fastapi:8080"
        )

    async def get_author(self, user_id: UUID) -> VersionAuthor:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/users/{user_id}"
            )

        if response.status_code != 200:
            return VersionAuthor(
                user_id=user_id,
                email="unknown"
            )

        data = response.json()

        return VersionAuthor(
            user_id=user_id,
            email=data["email"],
        )
