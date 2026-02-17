from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
import difflib

from infrastructure.db.models.document_version import DocumentVersion
from infrastructure.integrations.http_user_client import HttpUserClient


class DocumentNotFound(Exception):
    pass


class VersionConflict(Exception):
    pass


class DocumentVersionService:

    def __init__(self, db: AsyncSession, user_client: HttpUserClient):
        self.db = db
        self.user_client = user_client

    async def add_version(
        self,
        document_id: UUID,
        content: str,
        user_id: UUID,
        base_version_id: UUID | None,
    ):

        latest = await self.get_latest_version(document_id)

        if base_version_id is not None:
            if latest and latest.id != base_version_id:
                raise VersionConflict()

        version = DocumentVersion(
            document_id=document_id,
            content=content,
            created_by=user_id,
        )

        self.db.add(version)
        await self.db.commit()
        await self.db.refresh(version)

        return version

    async def get_versions(self, document_id: UUID, limit: int = 8):

        result = await self.db.execute(
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .order_by(desc(DocumentVersion.created_at))
            .limit(limit)
        )

        versions = result.scalars().all()

        response = []

        for v in versions:
            email = await self.user_client.get_user_email(v.created_by)

            response.append({
                "id": v.id,
                "document_id": v.document_id,
                "content": v.content,
                "created_by": v.created_by,
                "created_at": v.created_at,
                "author_email": email,
            })

        return response

    async def get_latest_version(self, document_id: UUID):

        result = await self.db.execute(
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .order_by(desc(DocumentVersion.created_at))
            .limit(1)
        )

        return result.scalar_one_or_none()

    async def revert_to_version(
        self,
        document_id: UUID,
        version_id: UUID,
        user_id: UUID,
    ):

        result = await self.db.execute(
            select(DocumentVersion).where(DocumentVersion.id == version_id)
        )

        version = result.scalar_one_or_none()

        if not version:
            raise DocumentNotFound()

        new_version = DocumentVersion(
            document_id=document_id,
            content=version.content,
            created_by=user_id,
        )

        self.db.add(new_version)
        await self.db.commit()
        await self.db.refresh(new_version)

        email = await self.user_client.get_user_email(user_id)

        return {
            "id": new_version.id,
            "document_id": new_version.document_id,
            "content": new_version.content,
            "created_by": new_version.created_by,
            "created_at": new_version.created_at,
            "author_email": email,
        }

    async def get_diff(self, document_id: UUID, version_id: UUID):

        result = await self.db.execute(
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .order_by(desc(DocumentVersion.created_at))
        )

        versions = result.scalars().all()

        for i, v in enumerate(versions):
            if v.id == version_id and i + 1 < len(versions):

                current = v.content
                previous = versions[i + 1].content

                diff = difflib.unified_diff(
                    previous.splitlines(),
                    current.splitlines(),
                    lineterm="",
                )

                return "\n".join(diff)

        return ""
