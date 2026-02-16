from fastapi import FastAPI
from api.routers.health import router as health_router
from api.routers.auth import router as auth_router

app = FastAPI(
    title="Auth Service"
)

app.include_router(health_router, prefix="/health")
app.include_router(auth_router, prefix="/auth")
