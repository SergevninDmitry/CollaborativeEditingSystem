from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from editing_system.fastapi_app.db.schemas import UserCreate, UserResponse
from editing_system.fastapi_app.dependencies import get_user_service
from editing_system.fastapi_app.services.user_service import (
    UserService,
    EmailAlreadyExists,
)

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
        service: UserService = Depends(get_user_service),
):
    return await service.get_all_users()
