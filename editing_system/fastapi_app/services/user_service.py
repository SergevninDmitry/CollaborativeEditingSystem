from uuid import uuid4, UUID
from typing import Dict
from editing_system.fastapi_app.db.schemas import (
    UserCreate,
    UserResponse
)
from editing_system.fastapi_app.db.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from editing_system.fastapi_app.services.security import hash_password


class EmailAlreadyExists(Exception):
    pass


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, data: UserCreate) -> User:
        # check unique email
        result = await self.db.execute(
            select(User).where(User.email == data.email)
        )
        existing = result.scalar_one_or_none()

        if existing:
            raise EmailAlreadyExists()

        user = User(
            email=data.email,
            password=hash_password(data.password),
            full_name=data.full_name
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def get_user(self, user_id: UUID) -> User | None:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_all_users(self) -> list[User]:
        result = await self.db.execute(
            select(User)
        )
        return result.scalars().all()
