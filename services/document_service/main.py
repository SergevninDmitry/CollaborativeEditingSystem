from fastapi import FastAPI
from api.documents import router as document_router
from infrastructure.db.base import Base
from infrastructure.db.session import engine
from api.health import router as health_router
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="Document Service",
    lifespan=lifespan
)

app.include_router(document_router, prefix="/documents")
app.include_router(health_router, prefix="/health")
