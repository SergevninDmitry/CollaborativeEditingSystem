from datetime import datetime, timedelta
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from services.user_service import UserService
from services.security import verify_password
from config import settings


class InvalidCredentials(Exception):
    pass


class AuthService:
    def __init__(self, db: AsyncSession):
        self.user_service = UserService(db)

    async def authenticate(self, email: str, password: str):
        user = await self.user_service.get_user_by_email(email)

        if not user:
            raise InvalidCredentials()

        if not verify_password(password, user.password):
            raise InvalidCredentials()

        return self.create_token(user.id)

    def create_token(self, user_id):
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        payload = {
            "sub": str(user_id),
            "exp": expire
        }

        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
