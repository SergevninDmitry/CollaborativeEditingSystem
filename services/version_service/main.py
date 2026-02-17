from fastapi import FastAPI
from api.routers.versions import router as versions_router
from infrastructure.db.base import Base
from infrastructure.db.session import engine
from api.routers.health import router as health_router
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="Version Service",
    lifespan=lifespan
)
app.include_router(versions_router, prefix="/versions")
app.include_router(health_router, prefix="/health")
