from datetime import datetime, timedelta
from jose import jwt
from clients.http_user_client import HttpUserClient
from shared.common.security.hashing import verify_password
from config import settings


class InvalidCredentials(Exception):
    pass


class AuthService:
    def __init__(self):
        self.user_client = HttpUserClient()

    async def authenticate(self, email: str, password: str):
        try:
            user = await self.user_client.get_user_by_email(email)

            if not user:
                raise InvalidCredentials()

            if not verify_password(password, user.password):
                raise InvalidCredentials()

            return self.create_token(user.id)
        except InvalidCredentials:
            raise InvalidCredentials()
        finally:
            await self.user_client.close()

    def create_token(self, user_id):
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        payload = {
            "sub": str(user_id),
            "exp": expire
        }

        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
