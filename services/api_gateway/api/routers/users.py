from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from dependencies import get_access_token, get_clients
from clients.registry import Clients
from shared.common.schemas.user import (
    UserCreate,
    UserResponse,
    UserUpdate,
    ChangePasswordRequest,
)
from utils.http import build_response

import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Users"])


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register user",
    description="Creates a new user account.",
    responses={
        201: {"description": "User successfully created"},
        400: {"description": "Email already exists"},
    },
)
async def register(
        data: UserCreate,
        clients: Clients = Depends(get_clients),
):
    logger.info(f"[USER REGISTER] email={data.email}")

    r = await clients.user.register(data.model_dump())

    if r.status_code != status.HTTP_201_CREATED:
        raise HTTPException(r.status_code, r.json())

    return build_response(r)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Returns authenticated user profile.",
)
async def get_me(
        token: str = Depends(get_access_token),
        clients: Clients = Depends(get_clients),
):
    logger.info("[USER GET ME]")

    r = await clients.user.get_me(token)

    if r.status_code != status.HTTP_200_OK:
        raise HTTPException(r.status_code, r.json())

    return build_response(r)


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update profile",
    description="Updates current user profile information.",
)
async def update_me(
        data: UserUpdate,
        token: str = Depends(get_access_token),
        clients: Clients = Depends(get_clients),
):
    logger.info("[USER UPDATE ME]")

    r = await clients.user.update_me(token, data.model_dump())

    if r.status_code != status.HTTP_200_OK:
        raise HTTPException(r.status_code, r.json())

    return build_response(r)


@router.post(
    "/me/change-password",
    summary="Change password",
    description="Changes password for authenticated user.",
    responses={
        200: {"description": "Password successfully changed"},
        404: {"description": "Invalid password or user not found"},
    },
)
async def change_password(
        data: ChangePasswordRequest,
        token: str = Depends(get_access_token),
        clients: Clients = Depends(get_clients),
):
    logger.info("[USER CHANGE PASSWORD]")

    r = await clients.user.change_password(token, data.model_dump())

    if r.status_code != status.HTTP_200_OK:
        raise HTTPException(r.status_code, r.json())

    return build_response(r)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Returns public user profile by user ID.",
)
async def get_user(
        user_id: UUID,
        token: str = Depends(get_access_token),
        clients: Clients = Depends(get_clients),
):
    logger.info(f"[USER GET] id={user_id}")

    r = await clients.user.get_user(token, str(user_id))

    if r.status_code != status.HTTP_200_OK:
        raise HTTPException(r.status_code, r.json())

    return build_response(r)
