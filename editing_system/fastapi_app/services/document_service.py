from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List

from editing_system.fastapi_app.db.models import (
    Document,
    DocumentVersion
)
from editing_system.fastapi_app.db.schemas import (
    DocumentCreate,
)
from sqlalchemy import desc
from fastapi import HTTPException, status
from uuid import UUID

class DocumentNotFound(Exception):
    pass


class DocumentService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_document(self, data: DocumentCreate, owner_id: str) -> Document:
        document = Document(
            title=data.title,
            owner_id=owner_id,
        )

        self.db.add(document)
        await self.db.flush()  # получаем document.id без commit

        first_version = DocumentVersion(
            document_id=document.id,
            content=data.content,
            created_by=owner_id,
        )

        self.db.add(first_version)

        await self.db.commit()
        await self.db.refresh(document)

        return document

    async def get_documents(self, owner_id: str) -> List[Document]:
        result = await self.db.execute(
            select(Document).where(Document.owner_id == owner_id)
        )
        return result.scalars().all()

    async def get_document(self, document_id: str) -> Document:
        result = await self.db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()

        if not document:
            raise DocumentNotFound()

        return document

    async def add_version(
            self,
            document_id: str,
            content: str,
            user_id: str,
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
        # print("----- ADD VERSION DEBUG -----")
        # print("LATEST VERSION ID:", latest_version.id if latest_version else None)
        # print("BASE VERSION ID:", base_version_id)
        # print("MATCH:", str(latest_version.id) == str(base_version_id) if latest_version else None)
        # print("--------------------------------")
        # если версия устарела → конфликт
        if latest_version and str(latest_version.id) != str(base_version_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Document was modified by another user",
            )

        new_version = DocumentVersion(
            document_id=document_id,
            content=content,
            created_by=user_id,
        )

        self.db.add(new_version)
        await self.db.commit()
        await self.db.refresh(new_version)

        return new_version

    async def get_versions(self, document_id: str):
        result = await self.db.execute(
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .order_by(desc(DocumentVersion.created_at))
        )

        return result.scalars().all()

    async def get_latest_version(self, document_id: str):
        result = await self.db.execute(
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .order_by(desc(DocumentVersion.created_at))
        )

        return result.scalars().first()

    async def revert_to_version(self, document_id: str, version_id: str, user_id: str):
        result = await self.db.execute(
            select(DocumentVersion).where(DocumentVersion.id == version_id)
        )
        version = result.scalar_one_or_none()

        if not version:
            raise DocumentNotFound()

        # создаём новую версию с тем же content
        new_version = DocumentVersion(
            document_id=document_id,
            content=version.content,
            created_by=user_id,
        )

        self.db.add(new_version)
        await self.db.commit()
        await self.db.refresh(new_version)

        return new_version
