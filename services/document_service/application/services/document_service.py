from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from infrastructure.db.models.document import Document
from infrastructure.db.models.document_share import DocumentShare
from shared.common.schemas.document import DocumentCreate
from fastapi import HTTPException
from uuid import UUID
from infrastructure.clients.http_version_client import HttpVersionClient


class DocumentNotFound(Exception):
    pass


class DocumentService:

    def __init__(self, db: AsyncSession, version_client: HttpVersionClient):
        self.db = db
        self.version_client = version_client

    async def create_document(
            self,
            data: DocumentCreate,
            owner_id: UUID,
            token: str,
    ) -> Document:

        document = Document(
            title=data.title,
            owner_id=owner_id,
        )

        self.db.add(document)

        try:
            await self.db.flush()
            await self.version_client.create_initial_version(
                document_id=document.id,
                content=data.content,
                user_id=owner_id,
                token=token,
            )
            await self.db.commit()
            await self.db.refresh(document)

        except Exception:
            await self.db.rollback()
            raise HTTPException(
                500,
                "Failed to create initial version"
            )
        return document

    async def get_documents(self, user_id: UUID):

        result = await self.db.execute(
            select(Document)
            .where(
                or_(
                    Document.owner_id == user_id,
                    Document.id.in_(
                        select(DocumentShare.document_id)
                        .where(DocumentShare.user_id == user_id)
                    )
                )
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
            raise HTTPException(
                status_code=403,
                detail="You are not the owner of the document",
            )

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
