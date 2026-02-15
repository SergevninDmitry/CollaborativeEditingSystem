from abc import ABC, abstractmethod
from uuid import UUID
from domains.versions.contracts import VersionAuthor


class UserGateway(ABC):

    @abstractmethod
    async def get_author(self, user_id: UUID) -> VersionAuthor:
        """
        Returns author info.
        Implementation may be local DB or remote HTTP service.
        """
        pass
