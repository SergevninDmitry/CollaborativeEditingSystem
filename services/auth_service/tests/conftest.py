from main import app
from httpx import AsyncClient
from uuid import uuid4

from shared.common.schemas.user import UserAuthData

from dependencies import get_auth_service
from application.services.auth_service import InvalidCredentials
import pytest


class FakeAuthService:

    def __init__(self, should_fail=False):
        self.should_fail = should_fail

    async def authenticate(self, email, password):
        if self.should_fail:
            raise InvalidCredentials()

        return "fake-token"


class FakeUserClient:

    def __init__(self, user=None):
        self.user = user
        self.closed = False

    async def get_user_by_email(self, email: str):
        return self.user

    async def close(self):
        self.closed = True


def make_user(password_hash: str):
    return UserAuthData(
        id=uuid4(),
        email="test@mail.com",
        password=password_hash,
    )


@pytest.fixture
def override_auth_service():
    def _override(should_fail=False):
        async def fake_dep():
            yield FakeAuthService(should_fail)

        app.dependency_overrides[get_auth_service] = fake_dep

    yield _override

    app.dependency_overrides.pop(get_auth_service, None)


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
