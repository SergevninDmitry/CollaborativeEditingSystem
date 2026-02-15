from fastapi import FastAPI
from config import setup_logging
from api.routers import (
    health,
    users,
    auth,
    documents
)
from domains.versions.router import router as versions_router
from db.base import Base
from db.session import engine


def create_app() -> FastAPI:
    app = FastAPI(
        title="Collaborative Editing System API",
        description="API for collaborative editing system"
    )

    routers = [
        (health.router, "/health"),
        (users.router, "/users"),
        (auth.router, "/auth"),
        (documents.router, "/documents"),
        (versions_router, "/versions")
    ]

    for router, prefix in routers:
        app.include_router(router, prefix=prefix)

    return app


setup_logging()
app = create_app()


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
