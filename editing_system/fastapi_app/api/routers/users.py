from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from editing_system.fastapi_app.db.schemas import (
    UserCreate,
    UserResponse,
    UserUpdate,
    ChangePasswordRequest
)
from editing_system.fastapi_app.dependencies import get_user_service, get_current_user
from editing_system.fastapi_app.services.user_service import (
    UserService,
    EmailAlreadyExists,
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
        data: UserCreate,
        service: UserService = Depends(get_user_service),
):
    try:
        return await service.create_user(data)
    except EmailAlreadyExists:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists",
        )


@router.put("/me", response_model=UserResponse)
async def update_me(
        data: UserUpdate,
        user_id: UUID = Depends(get_current_user),
        service: UserService = Depends(get_user_service),
):
    try:
        res = await service.update_user(user_id, data)
        logger.info(
            f"[update_me SUCCESS] data={data} user_id= {user_id}"
        )
        return res
    except EmailAlreadyExists:
        logger.error(
            f"[update_me FAILED] data={data} user_id= {user_id} e=User with this email already exists"
        )
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists",
        )
    except Exception as e:
        logger.error(
            f"[update_me FAILED] data={data} user_id= {user_id} e={e}"
        )
        raise HTTPException(
            status_code=400,
            detail="Update user failed",
        )


@router.post("/me/change-password")
async def change_password(
        data: ChangePasswordRequest,
        user_id: UUID = Depends(get_current_user),
        service: UserService = Depends(get_user_service),
):
    try:
        res = await service.change_password(
            user_id,
            data.old_password,
            data.new_password,
        )
        logger.info(
            f"[change_password SUCCESS] data={data} user_id= {user_id}"
        )
        return res
    except Exception as e:
        logger.error(
            f"[change_password FAILED] data={data} user_id= {user_id} e={e}"
        )
        raise HTTPException(
            status_code=400,
            detail="Change password failed",
        )



@router.get("/me", response_model=UserResponse)
async def get_me(
        user_id: UUID = Depends(get_current_user),
        service: UserService = Depends(get_user_service),
):
    user = await service.get_user(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
        user_id: UUID,
        service: UserService = Depends(get_user_service),
):
    user = await service.get_user(user_id)

    if not user:
        raise HTTPException(404, "User not found")

    return user


@router.get("/debug/all", response_model=list[UserResponse])
async def get_all_users(
        user_id: UUID = Depends(get_current_user),
        service: UserService = Depends(get_user_service),
):
    return await service.get_all_users()
