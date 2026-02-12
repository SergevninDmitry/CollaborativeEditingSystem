from uuid import uuid4, UUID
from typing import Dict
from editing_system.fastapi_app.schemas import (
    UserCreate,
    UserResponse
)


# Временная in-memory база
_FAKE_USERS: Dict[UUID, dict] = {}


def create_user(data: UserCreate) -> UserResponse:
    user_id = uuid4()

    user = {
        "id": user_id,
        "email": data.email,
        "password": data.password,   # потом заменим на хэш!
        "full_name": data.full_name,
    }

    _FAKE_USERS[user_id] = user

    return UserResponse(**user)


def get_user(user_id: UUID) -> UserResponse | None:
    user = _FAKE_USERS.get(user_id)
    if not user:
        return None

    return UserResponse(**user)
