from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from uuid import UUID

from config import settings
from infrastructure.db.session import get_session
from application.services.document_service import DocumentService
from infrastructure.clients.http_version_client import HttpVersionClient
from infrastructure.clients.http_user_client import HttpUserClient

security = HTTPBearer()


def get_user_client():
    return HttpUserClient()


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UUID:
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

        return UUID(payload["sub"])

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


async def get_access_token(
        credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    return credentials.credentials


def get_version_client():
    return HttpVersionClient()


async def get_document_service(
        db: AsyncSession = Depends(get_session),
        version_client: HttpVersionClient = Depends(get_version_client),
) -> DocumentService:
    return DocumentService(db, version_client)
