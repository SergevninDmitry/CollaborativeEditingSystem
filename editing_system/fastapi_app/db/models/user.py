from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from uuid import uuid4, UUID

from editing_system.fastapi_app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True
    )

    password: Mapped[str] = mapped_column(String(255))

    full_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )
