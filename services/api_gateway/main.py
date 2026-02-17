from fastapi import FastAPI

from api.routers.health import router as health_router
from api.routers.auth import router as auth_router
from api.routers.users import router as users_router
from api.routers.documents import router as documents_router
from api.routers.versions import router as versions_router
from contextlib import asynccontextmanager
from clients.registry import Clients


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
