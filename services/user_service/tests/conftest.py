import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.pool import StaticPool

from infrastructure.db.base import Base
from main import app
from dependencies import get_session, get_current_user
import uuid

DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    DATABASE_URL,
    future=True,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

TEST_USER_ID = uuid.uuid4()


async def _fake_user():
    return TEST_USER_ID


@pytest.fixture
def override_current_user():
    def _override(user_id):
        async def fake():
            return user_id

        app.dependency_overrides[get_current_user] = fake

    yield _override
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


@pytest.fixture()
async def db_session():
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()
        await session.close()


@pytest.fixture(autouse=True)
async def override_dependencies(db_session):
    async def _get_session_override():
        yield db_session

    app.dependency_overrides[get_session] = _get_session_override

    yield

    app.dependency_overrides.clear()


@pytest.fixture()
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
