from fastapi import APIRouter, Depends, HTTPException
from shared.common.schemas.auth import LoginRequest, TokenResponse
from application.services.auth_service import AuthService, InvalidCredentials
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Auth"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate user",
    description="""
Authenticate user using email and password.

Returns JWT access token used for authorization
in all protected endpoints.
""",
    responses={
        200: {
            "description": "Authentication successful",
        },
        401: {
            "description": "Invalid email or password",
        },
    },
    tags=["Auth"],
)
async def login(data: LoginRequest):
    """
    User login endpoint.
    """
    service = AuthService()

    logger.debug(f"Authenticating user with email: {data.email}")

    try:
        token = await service.authenticate(
            data.email,
            data.password,
        )

        return {"access_token": token}

    except InvalidCredentials:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

