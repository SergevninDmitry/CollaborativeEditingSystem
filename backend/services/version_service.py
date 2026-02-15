from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List

from db.models import (
    Document,
    DocumentVersion,
    User
)
from sqlalchemy import desc
from fastapi import HTTPException, status
from uuid import UUID
import difflib


class DocumentNotFound(Exception):
    pass


class VersionConflict(Exception):
    pass


class DocumentVersionService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_version(
            self,
            document_id: UUID,
            content: str,
            user_id: UUID,
            base_version_id: UUID,
    ):
        # получаем последнюю версию
        result = await self.db.execute(
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .order_by(desc(DocumentVersion.created_at))
            .limit(1)
        )

        latest_version = result.scalar_one_or_none()

        if latest_version and latest_version.id != base_version_id:
            raise VersionConflict()

        new_version = DocumentVersion(
            document_id=document_id,
            content=content,
            created_by=user_id,
        )

        self.db.add(new_version)
        await self.db.commit()
        await self.db.refresh(new_version)

        return new_version

    async def get_versions(self, document_id: UUID, limit: int = 8):

        result = await self.db.execute(
            select(DocumentVersion, User.email)
            .join(User, User.id == DocumentVersion.created_by)
            .where(DocumentVersion.document_id == document_id)
            .order_by(desc(DocumentVersion.created_at))
            .limit(limit)
        )

        rows = result.all()

        versions = []

        for version, email in rows:
            versions.append({
                "id": version.id,
                "document_id": version.document_id,
                "content": version.content,
                "created_by": version.created_by,
                "created_at": version.created_at,
                "author_email": email
            })

        return versions

    async def get_latest_version(self, document_id: UUID):
        result = await self.db.execute(
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .order_by(desc(DocumentVersion.created_at))
        )

        return result.scalars().first()

    async def revert_to_version(self, document_id: UUID, version_id: UUID, user_id: UUID):
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

        return new_version

    async def get_diff(self, document_id: UUID, version_id: UUID):

        versions = await self.get_versions(document_id)

        for i, v in enumerate(versions):
            if str(v["id"]) == str(version_id) and i + 1 < len(versions):
                current = v["content"]
                previous = versions[i + 1]["content"]

                diff = difflib.unified_diff(
                    previous.splitlines(),
                    current.splitlines(),
                    lineterm=""
                )

                return "\n".join(diff)

        return ""
