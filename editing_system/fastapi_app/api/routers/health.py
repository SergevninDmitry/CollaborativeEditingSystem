from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Health"]
)


@router.get("/")
async def health_check():
    logger.info("Health check")
    return {
        "status": "ok",
        "message": "service is running"
    }
