from fastapi import FastAPI
from api.routers.users import router as user_router
from db.base import Base
from db.session import engine
from api.routers.health import router as health_router
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="User Service",
    lifespan=lifespan
)

app.include_router(user_router, prefix="/users")
app.include_router(health_router, prefix="/health")
