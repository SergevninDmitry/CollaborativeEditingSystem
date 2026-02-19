import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.pool import StaticPool
from uuid import uuid4
from dependencies import get_current_user

from infrastructure.db.base import Base
from main import app

from dependencies import (
    get_session,
    get_current_user,
    get_document_service,
    get_user_client,
)

from application.services.document_service import DocumentService
from tests.fakes import FakeVersionClient, FakeUserClient

DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


@pytest.fixture()
async def db_session():
    async with SessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture(autouse=True)
async def override_dependencies(db_session):
    fake_version = FakeVersionClient()
    fake_user_client = FakeUserClient()

    async def _get_session_override():
        yield db_session

    async def _document_service_override():
        yield DocumentService(db_session, fake_version)

    async def _user_client_override():
        return fake_user_client

    app.dependency_overrides[get_session] = _get_session_override
    app.dependency_overrides[get_document_service] = _document_service_override
    app.dependency_overrides[get_user_client] = _user_client_override

    yield

    app.dependency_overrides.clear()


@pytest.fixture
def override_current_user():
    def _override(user_id):
        async def fake_user():
            return user_id

        app.dependency_overrides[get_current_user] = fake_user

    yield _override

    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture()
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
