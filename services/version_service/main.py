from fastapi import FastAPI
from domains.versions.router import router as versions_router
from db.base import Base
from db.session import engine
from api.health import router as health_router

app = FastAPI(title="Version Service")

app.include_router(versions_router, prefix="/versions")
app.include_router(health_router, prefix="/health")


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
