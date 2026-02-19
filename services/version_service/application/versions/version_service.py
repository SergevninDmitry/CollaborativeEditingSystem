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

        if not versions:
            return []

        user_ids = list({v.created_by for v in versions})
        emails_map = await self.user_client.get_users_batch(user_ids)

        response = []

        for v in versions:
            response.append({
                "id": v.id,
                "document_id": v.document_id,
                "content": v.content,
                "created_by": v.created_by,
                "created_at": v.created_at,
                "author_email": emails_map.get(v.created_by),
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

        if not versions:
            return ""

        latest = versions[0]

        selected = next(
            (v for v in versions if v.id == version_id),
            None
        )

        if not selected:
            return ""

        if selected.id == latest.id:
            return ""

        diff = difflib.unified_diff(
            selected.content.splitlines(),
            latest.content.splitlines(),
            fromfile="selected",
            tofile="latest",
            lineterm="",
        )

        return "\n".join(diff)
