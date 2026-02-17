from fastapi import APIRouter, Depends, HTTPException
from shared.common.schemas.auth import LoginRequest, TokenResponse
from application.services.auth_service import AuthService, InvalidCredentials
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    service = AuthService()
    logger.debug(f"Authenticating user with email: {data.email}")

    try:
        token = await service.authenticate(
            data.email,
            data.password
        )
        return {"access_token": token}
    except InvalidCredentials:
        raise HTTPException(401, "Invalid credentials")
