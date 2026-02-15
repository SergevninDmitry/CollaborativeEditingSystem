from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from domains.versions.service import DocumentVersionService


class VersionClient:
    """
    Abstract boundary between Document domain
    and Version domain.
    """

    async def create_initial_version(
            self,
            document_id: UUID,
            content: str,
            user_id: UUID,
            token: str,
    ):
        raise NotImplementedError


class LocalVersionClient(VersionClient):

    def __init__(self, service: DocumentVersionService):
        self.service = service

    async def create_initial_version(
            self,
            document_id: UUID,
            content: str,
            user_id: UUID,
            token: str
    ):
        # первая версия не имеет конфликта
        return await self.service.add_version(
            document_id=document_id,
            content=content,
            user_id=user_id,
            base_version_id=None,
        )
