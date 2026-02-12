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

    async def add_version(self, document_id: str, content: str, user_id: str):
        version = DocumentVersion(
            document_id=document_id,
            content=content,
            created_by=user_id,
        )

        self.db.add(version)
        await self.db.commit()
        await self.db.refresh(version)

        return version

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
