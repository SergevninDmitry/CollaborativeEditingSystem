from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends

from fastapi import Request
from clients.registry import Clients

security = HTTPBearer()


def get_clients(request: Request) -> Clients:
    return request.app.state.clients


async def get_access_token(
        credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    return credentials.credentials
