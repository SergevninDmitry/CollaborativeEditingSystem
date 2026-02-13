from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from uuid import uuid4

from editing_system.fastapi_app.db.base import Base


class DocumentShare(Base):
    __tablename__ = "document_shares"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    document_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("documents.id", ondelete="CASCADE")
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE")
    )
