from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, status, Header, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from uuid import UUID

from db.session import get_session
from services.user_service import UserService, UserNotFound
from config import settings

security = HTTPBearer()


async def verify_internal(x_service_token: str = Header(...)):
    if x_service_token != settings.INTERNAL_SERVICE_TOKEN:
        raise HTTPException(403, "Forbidden")


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

        user_id = UUID(payload["sub"])

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        return user_id

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


async def get_user_service(
        db: AsyncSession = Depends(get_session),
) -> UserService:
    return UserService(db)


async def get_access_token(
        credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    return credentials.credentials
