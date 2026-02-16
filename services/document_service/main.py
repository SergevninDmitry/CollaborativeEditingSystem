from fastapi import FastAPI
from domains.documents.router import router as document_router
from db.base import Base
from db.session import engine
from api.health import router as health_router
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Document Service",
    lifespan=lifespan
)

app.include_router(document_router, prefix="/documents")
app.include_router(health_router, prefix="/health")
