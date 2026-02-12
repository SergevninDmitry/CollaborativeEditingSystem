from fastapi import FastAPI
from editing_system.fastapi_app.config import setup_logging
from editing_system.fastapi_app.api.routers import (
    health,
    users,
    auth,
    documents
)
from editing_system.fastapi_app.db.base import Base
from editing_system.fastapi_app.db.session import engine
from editing_system.fastapi_app.db.models import User, Document, DocumentVersion


def create_app() -> FastAPI:
    app = FastAPI(
        title="Collaborative Editing System API",
        description="API for collaborative editing system"
    )

    routers = [
        (health.router, "/health"),
        (users.router, "/users"),
        (auth.router, "/auth"),
        (documents.router, "/documents")
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
