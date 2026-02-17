from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID
from pydantic import EmailStr

from shared.common.schemas.user import (
    UserCreate,
    UserResponse,
    UserUpdate,
    ChangePasswordRequest,
)

from dependencies import (
    get_user_service,
    get_current_user,
    verify_internal,
)

from application.services.user_service import (
    UserService,
    EmailAlreadyExists,
    UserNotFound,
    InvalidPassword,
)

import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Users"])


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="""
Creates a new user account.

Email must be unique across the system.
""",
    responses={
        201: {"description": "User successfully created"},
        400: {"description": "Email already exists"},
    },
)
async def create_user(
        data: UserCreate,
        service: UserService = Depends(get_user_service),
):
    """
    Register a new user.
    """
    try:
        return await service.create_user(data)

    except EmailAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )


@router.get(
    "/internal/auth-data",
    summary="Get authentication data (internal)",
    description="""
⚠ INTERNAL ENDPOINT.

Used by Auth Service to retrieve user credentials.
Requires internal service token.
""",
    responses={
        200: {"description": "Authentication data returned"},
        403: {"description": "Forbidden (invalid internal token)"},
        404: {"description": "User not found"},
    },
)
async def get_auth_data(
        email: EmailStr = Query(...),
        _=Depends(verify_internal),
        service: UserService = Depends(get_user_service),
):
    """
    Internal endpoint used for authentication validation.
    """
    user = await service.get_user_by_email(email)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "email": user.email,
        "password": user.password,
    }


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user profile",
    description="Updates profile information of the authenticated user.",
    responses={
        200: {"description": "Profile updated successfully"},
        400: {"description": "Invalid update request"},
        401: {"description": "Unauthorized"},
    },
)
async def update_me(
        data: UserUpdate,
        user_id: UUID = Depends(get_current_user),
        service: UserService = Depends(get_user_service),
):
    """
    Update profile data of current user.
    """
    try:
        res = await service.update_user(user_id, data)

        logger.info(
            f"[update_me SUCCESS] data={data} user_id={user_id}"
        )

        return res

    except EmailAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    except Exception as e:
        logger.error(
            f"[update_me FAILED] user_id={user_id} error={e}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Update user failed",
        )


@router.post(
    "/me/change-password",
    summary="Change user password",
    description="Changes password for the authenticated user.",
    responses={
        200: {"description": "Password updated successfully"},
        404: {"description": "User not found or invalid password"},
    },
)
async def change_password(
        data: ChangePasswordRequest,
        user_id: UUID = Depends(get_current_user),
        service: UserService = Depends(get_user_service),
):
    """
    Change password of the current user.
    """
    try:
        return await service.change_password(
            user_id,
            data.old_password,
            data.new_password,
        )

    except UserNotFound:
        raise HTTPException(404, "User not found")

    except InvalidPassword:
        raise HTTPException(404, "Invalid password")

    except Exception as e:
        logger.error(
            f"[change_password FAILED] user_id={user_id} error={e}"
        )
        raise HTTPException(
            status_code=400,
            detail="Change password failed",
        )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Returns profile information of the authenticated user.",
)
async def get_me(
        user_id: UUID = Depends(get_current_user),
        service: UserService = Depends(get_user_service),
):
    """
    Retrieve current authenticated user.
    """
    user = await service.get_user(user_id)

    if not user:
        raise HTTPException(404, "User not found")

    return user


@router.get(
    "/debug/all",
    response_model=list[UserResponse],
    summary="List all users (debug)",
    description="Debug endpoint returning all users. Should be disabled in production.",
)
async def get_all_users(
        user_id: UUID = Depends(get_current_user),
        service: UserService = Depends(get_user_service),
):
    return await service.get_all_users()


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Returns public information about a user.",
    responses={
        404: {"description": "User not found"},
    },
)
async def get_user(
        user_id: UUID,
        service: UserService = Depends(get_user_service),
):
    user = await service.get_user(user_id)

    if not user:
        raise HTTPException(404, "User not found")

    return user
