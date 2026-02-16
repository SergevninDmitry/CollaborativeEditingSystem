import httpx
import os
from uuid import UUID


class HttpVersionClient:

    def __init__(self):
        self.url = os.getenv(
            "VERSION_SERVICE_URL",
            "http://version_service:8001"
        )

    async def create_initial_version(
            self,
            document_id: UUID,
            content: str,
            user_id: UUID,
            token: str
    ):
        async with httpx.AsyncClient(
                timeout=httpx.Timeout(5.0)
        ) as client:
            try:
                response = await client.post(
                    f"{self.url}/versions/{document_id}/versions",
                    json={
                        "content": content,
                        "base_version_id": None
                    },
                    headers={
                        "Authorization": f"Bearer {token}"
                    }
                )
                response.raise_for_status()
            except httpx.RequestError:
                raise Exception("Version service unavailable")

        response.raise_for_status()
        return response.json()
