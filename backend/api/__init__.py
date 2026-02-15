from api.routers.health import router as health
from api.routers.users import router as users
from api.routers.auth import router as auth
from api.routers.documents import router as documents

__all__ = [
    "health",
    "users",
    "auth",
    "documents"
]
