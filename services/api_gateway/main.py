from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging

from api.routers.health import router as health_router
from api.routers.auth import router as auth_router
from api.routers.users import router as users_router
from api.routers.documents import router as documents_router
from api.routers.versions import router as versions_router
from contextlib import asynccontextmanager
from clients.registry import Clients

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.clients = Clients()
    yield
    await app.state.clients.close()


app = FastAPI(
    title="API Gateway",
    lifespan=lifespan
)

app.include_router(health_router, prefix="/health")
app.include_router(auth_router, prefix="/auth")
app.include_router(users_router, prefix="/users")
app.include_router(documents_router, prefix="/documents")
app.include_router(versions_router, prefix="/versions")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error")

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error"
        },
    )
