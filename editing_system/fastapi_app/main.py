from fastapi import FastAPI
from editing_system.fastapi_app.config import setup_logging
from editing_system.fastapi_app.api.routers import (
    health,
    users
)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Collaborative Editing System API",
        description="API for collaborative editing system"
    )

    routers = [
        (health.router, "/api/health"),
        (users.router, "/api/users")
    ]

    for router, prefix in routers:
        app.include_router(router, prefix=prefix)

    return app


setup_logging()
app = create_app()