from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging
from api.routers.health import router as health_router
from api.routers.auth import router as auth_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Auth Service"
)

app.include_router(health_router, prefix="/health")
app.include_router(auth_router, prefix="/auth")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error")

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error"
        },
    )
