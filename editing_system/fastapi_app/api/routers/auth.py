from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from editing_system.fastapi_app.db.session import get_session
from editing_system.fastapi_app.db.schemas import LoginRequest, TokenResponse
from editing_system.fastapi_app.services.auth_service import AuthService, InvalidCredentials
from editing_system.fastapi_app.dependencies import get_current_user

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
        user_id: str = Depends(get_current_user)
):
    return {"message": f"You are {user_id}"}
