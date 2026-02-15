from domains.versions.repository import VersionRepository
from uuid import UUID
import difflib


class DocumentNotFound(Exception):
    pass


class VersionConflict(Exception):
    pass


class DocumentVersionService:

    def __init__(self, repo: VersionRepository):
        self.repo = repo

    async def add_version(
            self,
            document_id: UUID,
            content: str,
            user_id: UUID,
            base_version_id: UUID,
    ):
        latest_version = await self.repo.get_latest(document_id)

        if latest_version and latest_version.id != base_version_id:
            raise VersionConflict()

        return await self.repo.create(
            document_id,
            content,
            user_id,
        )

    async def get_versions(self, document_id: UUID, limit: int = 8):

        versions = await self.repo.get_versions(document_id, limit)

        return [
            {
                "id": v.id,
                "document_id": v.document_id,
                "content": v.content,
                "created_by": v.created_by,
                "created_at": v.created_at,
            }
            for v in versions
        ]

    async def get_latest_version(self, document_id: UUID):
        return await self.repo.get_latest(document_id)

    async def revert_to_version(
            self,
            document_id: UUID,
            version_id: UUID,
            user_id: UUID,
    ):

        version = await self.repo.get_by_id(version_id)

        if not version:
            raise DocumentNotFound()

        return await self.repo.create(
            document_id,
            version.content,
            user_id,
        )

    async def get_diff(self, document_id: UUID, version_id: UUID):

        versions = await self.get_versions(document_id)

        for i, v in enumerate(versions):
            if str(v["id"]) == str(version_id) and i + 1 < len(versions):

                current = v["content"]
                previous = versions[i + 1]["content"]

                diff = difflib.unified_diff(
                    previous.splitlines(),
                    current.splitlines(),
                    lineterm="",
                )

                return "\n".join(diff)

        return ""
