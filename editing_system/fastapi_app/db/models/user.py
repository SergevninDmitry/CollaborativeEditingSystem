from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4, UUID as PyUUID
from editing_system.fastapi_app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True
    )

    about_user: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    password: Mapped[str] = mapped_column(String(255))

    full_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )
