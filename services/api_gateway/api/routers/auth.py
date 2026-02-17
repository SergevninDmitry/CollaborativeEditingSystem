from fastapi import APIRouter, HTTPException, Depends
from shared.common.schemas.auth import LoginRequest
from utils.http import build_response
from dependencies import get_clients
from clients.registry import Clients
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Auth"])


@router.post("/login")
async def login(
    data: LoginRequest,
    clients: Clients = Depends(get_clients)

):
    logger.info(f"login auth_client data={data}")
    r = await clients.auth.login(data.model_dump())
    logger.info(f"login auth_client r={r}")

    if r.status_code != 200:
        raise HTTPException(
            status_code=r.status_code,
            detail=r.json()
        )

    return build_response(r)
