from fastapi import APIRouter, HTTPException, Depends, status
from shared.common.schemas.auth import (
    LoginRequest,
    TokenResponse,
)
from utils.http import build_response
from dependencies import get_clients
from clients.registry import Clients
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Auth"])


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User authentication",
    description="""
Authenticates user credentials via Auth Service
and returns JWT access token.

This endpoint is exposed through API Gateway and
proxies request to the authentication microservice.
""",
    responses={
        200: {"description": "Successful authentication"},
        401: {"description": "Invalid credentials"},
        500: {"description": "Authentication service error"},
    },
)
async def login(
    data: LoginRequest,
    clients: Clients = Depends(get_clients),
):
    """
    Authenticate user and return access token.
    """

    logger.info(f"[AUTH LOGIN] email={data.email}")

    response = await clients.auth.login(data.model_dump(mode="json"))

    logger.info(f"[AUTH RESPONSE] status={response.status_code}")

    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.json(),
        )

    return build_response(response)
