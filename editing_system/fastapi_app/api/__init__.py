from editing_system.fastapi_app.api.routers.health import router as health
from editing_system.fastapi_app.api.routers.users import router as users
from editing_system.fastapi_app.api.routers.auth import router as auth


__all__ = [
    "health",
    "users",
    "auth"
]
