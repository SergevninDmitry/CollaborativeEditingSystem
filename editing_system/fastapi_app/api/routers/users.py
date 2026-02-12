from fastapi import APIRouter, HTTPException
from uuid import UUID

from editing_system.fastapi_app.schemas import UserCreate, UserResponse
from editing_system.fastapi_app.services import user_service


router = APIRouter(tags=["users"])


@router.post("/", response_model=UserResponse)
async def create_user(data: UserCreate):
    return user_service.create_user(data)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID):
    user = user_service.get_user(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
