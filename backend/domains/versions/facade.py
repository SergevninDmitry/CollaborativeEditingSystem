from uuid import UUID
from typing import List

from domains.versions.service import DocumentVersionService
from services.user_service import UserService
from domains.versions.schemas import DocumentVersionResponse


class VersionFacade:
    """
    Application layer.
    Orchestrates multiple domain services.
    """

    def __init__(
        self,
        version_service: DocumentVersionService,
        user_service: UserService,
    ):
        self.version_service = version_service
        self.user_service = user_service

    async def get_versions(self, document_id: UUID) -> List[DocumentVersionResponse]:

        versions = await self.version_service.get_versions(document_id)

        result = []

        for v in versions:
            user = await self.user_service.get_user(v["created_by"])

            author_email = user.email if user else "unknown"

            result.append(
                DocumentVersionResponse(
                    id=v["id"],
                    document_id=v["document_id"],
                    content=v["content"],
                    created_by=v["created_by"],
                    created_at=v["created_at"],
                    author_email=author_email,
                )
            )

        return result
