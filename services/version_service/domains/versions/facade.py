from uuid import UUID
from typing import List

from domains.versions.service import DocumentVersionService
from domains.versions.schemas import DocumentVersionResponse
from domains.versions.gateways.user_gateway import UserGateway


class VersionFacade:
    """
    Application layer.
    Orchestrates domain + external services.
    """

    def __init__(
        self,
        version_service: DocumentVersionService,
        user_gateway: UserGateway,
    ):
        self.version_service = version_service
        self.user_gateway = user_gateway

    async def get_versions(self, document_id: UUID) -> List[DocumentVersionResponse]:

        versions = await self.version_service.get_versions(document_id)

        result = []

        for v in versions:
            author = await self.user_gateway.get_author(v["created_by"])

            result.append(
                DocumentVersionResponse(
                    id=v["id"],
                    document_id=v["document_id"],
                    content=v["content"],
                    created_by=v["created_by"],
                    created_at=v["created_at"],
                    author_email=author.email,
                )
            )

        return result
