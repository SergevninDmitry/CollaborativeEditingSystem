from fastapi import APIRouter, Depends, HTTPException
from dependencies import get_access_token
from clients.http_user_client import UserClient
from shared.common.schemas.user import *
from utils.http import build_response



router = APIRouter(tags=["Users"])
client = UserClient()


@router.post("/", response_model=UserResponse)
async def register(data: UserCreate):
    r = await client.register(data.model_dump())

    if r.status_code >= 400:
        raise HTTPException(r.status_code, r.text)

    return build_response(r)


@router.get("/me")
async def get_me(token: str = Depends(get_access_token)):
    r = await client.get_me(token)
    return build_response(r)


@router.put("/me")
async def update_me(
    data: UserUpdate,
    token: str = Depends(get_access_token),
):
    r = await client.update_me(token, data.model_dump())
    return build_response(r)


@router.post("/me/change-password")
async def change_password(
    data: ChangePasswordRequest,
    token: str = Depends(get_access_token),
):
    r = await client.change_password(token, data.model_dump())
    return build_response(r)


@router.get("/{user_id}")
async def get_user(
    user_id: str,
    token: str = Depends(get_access_token),
):
    r = await client.get_user(token, user_id)
    return build_response(r)
