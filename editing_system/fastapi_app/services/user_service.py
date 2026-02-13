from uuid import uuid4, UUID
from typing import Dict
from editing_system.fastapi_app.db.schemas import (
    UserCreate,
    UserResponse,
    UserUpdate
)
from editing_system.fastapi_app.db.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from editing_system.fastapi_app.services.security import (
    hash_password,
    verify_password
)
from fastapi import HTTPException

import logging


logger = logging.getLogger(__name__)

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

    async def update_user(self, user_id: UUID, data: UserUpdate):
        logger.info(f"user_service update_user user_id={user_id}")
        user = await self.get_user(user_id)

        logger.info(f"user_service update_user user={user}")
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if data.full_name is not None:
            user.full_name = data.full_name

        if data.about_user is not None:
            user.about_user = data.about_user

        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def change_password(self, user_id: UUID, old_password: str, new_password: str):
        logger.info(f"change_password update_user user_id={user_id}")
        user = await self.get_user(user_id)

        logger.info(f"change_password update_user user={user}")
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not verify_password(old_password, user.password):
            raise HTTPException(status_code=400, detail="Wrong password")

        user.password = hash_password(new_password)

        await self.db.commit()

        return {"message": "Password updated"}
