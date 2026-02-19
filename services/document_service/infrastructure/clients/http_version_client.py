import httpx
from uuid import UUID
from config import settings


class VersionServiceUnavailable(Exception):
    pass


class VersionServiceError(Exception):
    pass


class HttpVersionClient:

    def __init__(self):
        self.url = settings.VERSION_SERVICE_URL
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(5.0)
        )

    async def create_initial_version(
            self,
            document_id: UUID,
            content: str,
            user_id: UUID,
            token: str
    ):
        try:
            response = await self.client.post(
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

        except httpx.TimeoutException:
            raise VersionServiceUnavailable("Timeout")

        except httpx.RequestError:
            raise VersionServiceUnavailable()

        except httpx.HTTPStatusError as e:
            raise VersionServiceError(e.response.text)

        return response.json()
