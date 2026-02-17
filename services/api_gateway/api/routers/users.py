from fastapi import APIRouter, Depends, HTTPException
from dependencies import get_access_token
from shared.common.schemas.user import *
from utils.http import build_response
from dependencies import get_clients
from clients.registry import Clients

router = APIRouter(tags=["Users"])


@router.post("/", response_model=UserResponse)
async def register(
        data: UserCreate,
        clients: Clients = Depends(get_clients),
):
    r = await clients.user.register(data.model_dump())

    if r.status_code >= 400:
        raise HTTPException(r.status_code, r.text)

    return build_response(r)


@router.get("/me")
async def get_me(
        token: str = Depends(get_access_token),
        clients: Clients = Depends(get_clients)
):
    r = await clients.user.get_me(token)
    return build_response(r)


@router.put("/me")
async def update_me(
        data: UserUpdate,
        token: str = Depends(get_access_token),
        clients: Clients = Depends(get_clients),
):
    r = await clients.user.update_me(token, data.model_dump())
    return build_response(r)


@router.post("/me/change-password")
async def change_password(
        data: ChangePasswordRequest,
        token: str = Depends(get_access_token),
        clients: Clients = Depends(get_clients),
):
    r = await clients.user.change_password(token, data.model_dump())
    return build_response(r)


@router.get("/{user_id}")
async def get_user(
        user_id: str,
        token: str = Depends(get_access_token),
        clients: Clients = Depends(get_clients),
):
    r = await clients.user.get_user(token, user_id)
    return build_response(r)
