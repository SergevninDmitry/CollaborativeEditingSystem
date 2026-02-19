import pytest

from application.services.auth_service import (
    AuthService,
    InvalidCredentials,
)
from jose import jwt
from config import settings

from tests.conftest import FakeUserClient, make_user


@pytest.mark.asyncio
async def test_authenticate_success(monkeypatch):
    from shared.common.security.hashing import hash_password

    user = make_user(hash_password("secret"))

    fake_client = FakeUserClient(user)

    service = AuthService()
    service.user_client = fake_client

    token = await service.authenticate("test@mail.com", "secret")

    assert isinstance(token, str)
    assert fake_client.closed is True


@pytest.mark.asyncio
async def test_authenticate_user_not_found():
    fake_client = FakeUserClient(None)

    service = AuthService()
    service.user_client = fake_client

    with pytest.raises(InvalidCredentials):
        await service.authenticate("missing@mail.com", "123")


@pytest.mark.asyncio
async def test_authenticate_user_not_found():
    fake_client = FakeUserClient(None)

    service = AuthService()
    service.user_client = fake_client

    with pytest.raises(InvalidCredentials):
        await service.authenticate("missing@mail.com", "123")


@pytest.mark.asyncio
async def test_token_contains_user_id():
    from shared.common.security.hashing import hash_password

    user = make_user(hash_password("secret"))

    fake_client = FakeUserClient(user)

    service = AuthService()
    service.user_client = fake_client

    token = await service.authenticate("test@mail.com", "secret")

    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )

    assert payload["sub"] == str(user.id)
