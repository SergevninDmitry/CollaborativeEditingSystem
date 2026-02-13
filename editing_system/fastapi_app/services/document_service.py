from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List

from editing_system.fastapi_app.db.models import (
    Document,
    DocumentVersion,
    User,
    DocumentShare
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

    async def get_documents(self, user_id: str):

        result = await self.db.execute(
            select(Document)
            .outerjoin(DocumentShare, Document.id == DocumentShare.document_id)
            .where(
                (Document.owner_id == user_id)
                | (DocumentShare.user_id == user_id)
            )
        )

        return result.scalars().unique().all()

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
        print("LATEST:", str(latest_version.id))
        print("BASE:", str(base_version_id))
        print("EQUAL:", str(latest_version.id) == str(base_version_id))

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
            select(DocumentVersion, User.email)
            .join(User, User.id == DocumentVersion.created_by)
            .where(DocumentVersion.document_id == document_id)
            .order_by(desc(DocumentVersion.created_at))
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

        new_version = DocumentVersion(
            document_id=document_id,
            content=version.content,
            created_by=user_id,
        )

        self.db.add(new_version)
        await self.db.commit()
        await self.db.refresh(new_version)

        return new_version

    async def share_document(
            self,
            document_id: str,
            owner_id: str,
            target_user_id: str
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
