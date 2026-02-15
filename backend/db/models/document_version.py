from sqlalchemy import String, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4, UUID as PyUUID
from db.base import Base


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    document_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id"),
        index=True
    )

    content: Mapped[str] = mapped_column(Text)

    created_by: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
