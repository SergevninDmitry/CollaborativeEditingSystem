from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_session
from db.schemas import LoginRequest, TokenResponse
from services.auth_service import AuthService, InvalidCredentials
from dependencies import get_current_user
from uuid import UUID

router = APIRouter(tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
        data: LoginRequest,
        db: AsyncSession = Depends(get_session)
):
    service = AuthService(db)

    try:
        token = await service.authenticate(data.email, data.password)
        return {"access_token": token}
    except InvalidCredentials:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@router.get("/protected")
async def protected_route(
        user_id: UUID = Depends(get_current_user)
):
    return {"message": f"You are {user_id}"}
