from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List

from db.models import (
    Document,
    DocumentVersion,
    User,
    DocumentShare
)
from db.schemas import (
    DocumentCreate,
)
from sqlalchemy import desc
from fastapi import HTTPException, status
from uuid import UUID
import difflib


class DocumentNotFound(Exception):
    pass


class DocumentService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_document(self, data: DocumentCreate, owner_id: UUID) -> Document:
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

    async def get_documents(self, user_id: UUID):

        result = await self.db.execute(
            select(Document)
            .outerjoin(DocumentShare, Document.id == DocumentShare.document_id)
            .where(
                (Document.owner_id == user_id)
                | (DocumentShare.user_id == user_id)
            )
        )

        return result.scalars().unique().all()

    async def get_document(self, document_id: UUID) -> Document:
        result = await self.db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()

        if not document:
            raise DocumentNotFound()

        return document

    async def share_document(
            self,
            document_id: UUID,
            owner_id: UUID,
            target_user_id: UUID
    ):

        document = await self.get_document(document_id)

        if document.owner_id != owner_id:
            raise HTTPException(status_code=403, detail="Not owner")

        result = await self.db.execute(
            select(DocumentShare).where(
                DocumentShare.document_id == document_id,
                DocumentShare.user_id == target_user_id
            )
        )

        if result.scalar_one_or_none():
            return {"message": "Already shared"}

        share = DocumentShare(
            document_id=document_id,
            user_id=target_user_id
        )

        self.db.add(share)
        await self.db.commit()

        return {"message": "Document shared successfully"}
