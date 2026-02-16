from fastapi import APIRouter, HTTPException
from clients.http_auth_client import AuthClient
from shared.common.schemas.auth import LoginRequest
from utils.http import build_response


router = APIRouter(tags=["Auth"])
client = AuthClient()


@router.post("/login")
async def login(data: LoginRequest):
    r = await client.login(data.model_dump())

    if r.status_code != 200:
        raise HTTPException(r.status_code, r.text)

    return build_response(r)
