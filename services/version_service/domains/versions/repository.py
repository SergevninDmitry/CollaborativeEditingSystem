from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from db.models.document_version import DocumentVersion


class VersionRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_latest(self, document_id: UUID):
        result = await self.db.execute(
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .order_by(desc(DocumentVersion.created_at))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        document_id: UUID,
        content: str,
        user_id: UUID,
    ):
        version = DocumentVersion(
            document_id=document_id,
            content=content,
            created_by=user_id,
        )

        self.db.add(version)
        await self.db.commit()
        await self.db.refresh(version)

        return version

    async def get_versions(self, document_id: UUID, limit: int):
        result = await self.db.execute(
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .order_by(desc(DocumentVersion.created_at))
            .limit(limit)
        )

        return result.scalars().all()

    async def get_by_id(self, version_id: UUID):
        result = await self.db.execute(
            select(DocumentVersion)
            .where(DocumentVersion.id == version_id)
        )
        return result.scalar_one_or_none()
