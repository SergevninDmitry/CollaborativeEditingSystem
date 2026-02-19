from api.documents import router as document_router
from infrastructure.db.base import Base
from infrastructure.db.session import engine
from api.health import router as health_router
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


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


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error")

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error"
        },
    )
