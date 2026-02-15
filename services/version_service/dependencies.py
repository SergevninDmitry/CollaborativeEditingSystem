from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from uuid import UUID
from config import settings
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_session
from domains.versions.repository import VersionRepository
from domains.versions.service import DocumentVersionService
from domains.versions.facade import VersionFacade

from integrations.http_user_gateway import HttpUserGateway
from domains.versions.gateways.user_gateway import UserGateway

# переключатель режима
USE_REMOTE_USER_SERVICE = True


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


async def get_version_repository(
        db: AsyncSession = Depends(get_session),
) -> VersionRepository:
    return VersionRepository(db)


async def get_version_service(
        repo: VersionRepository = Depends(get_version_repository),
) -> DocumentVersionService:
    return DocumentVersionService(repo)


async def get_user_gateway() -> UserGateway:
    return HttpUserGateway()


async def get_version_facade(
    version_service: DocumentVersionService = Depends(get_version_service),
    user_gateway: UserGateway = Depends(get_user_gateway),
) -> VersionFacade:
    return VersionFacade(version_service, user_gateway)

