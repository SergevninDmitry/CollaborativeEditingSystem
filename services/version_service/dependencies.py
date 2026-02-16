from integrations.http_user_gateway import HttpUserGateway
from domains.versions.facade import VersionFacade
from domains.versions.service import DocumentVersionService
from domains.versions.repository import VersionRepository
from db.session import get_session
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from fastapi import HTTPException, status
from uuid import UUID
from config import settings

security = HTTPBearer()


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

        user_id = UUID(payload["sub"])

        return user_id

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


async def get_repository(
        db: AsyncSession = Depends(get_session),
):
    return VersionRepository(db)


async def get_version_service(
        repo: VersionRepository = Depends(get_repository),
):
    return DocumentVersionService(repo)


user_gateway = HttpUserGateway()


async def get_user_gateway():
    return user_gateway


async def get_version_facade(
        service: DocumentVersionService = Depends(get_version_service),
        user_gateway=Depends(get_user_gateway),
):
    return VersionFacade(service, user_gateway)
