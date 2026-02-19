import pytest
from uuid import uuid4

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.pool import StaticPool

from infrastructure.db.base import Base
from application.services.user_service import (
    UserService,
    EmailAlreadyExists,
    InvalidPassword,
)

from shared.common.schemas.user import UserCreate, UserUpdate

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


@pytest.fixture(scope="module", autouse=True)
async def prepare_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


@pytest.fixture()
async def session():
    async with SessionLocal() as s:
        yield s
        await s.rollback()


@pytest.fixture()
async def service(session):
    return UserService(session)


@pytest.mark.asyncio
async def test_create_user(service):
    data = UserCreate(
        email="test@mail.com",
        password="123456",
        full_name="John",
    )

    user = await service.create_user(data)

    assert user.email == "test@mail.com"
    assert user.password != "123456"  # hashed


@pytest.mark.asyncio
async def test_create_user_duplicate_email(service):
    data = UserCreate(
        email="dup@mail.com",
        password="123",
        full_name="User",
    )

    await service.create_user(data)

    with pytest.raises(EmailAlreadyExists):
        await service.create_user(data)


@pytest.mark.asyncio
async def test_get_user(service):
    data = UserCreate(
        email="get@mail.com",
        password="123",
        full_name="User",
    )

    user = await service.create_user(data)

    fetched = await service.get_user(user.id)

    assert fetched.id == user.id


@pytest.mark.asyncio
async def test_update_user(service):
    user = await service.create_user(
        UserCreate(
            email="update@mail.com",
            password="123",
            full_name="Old",
        )
    )

    updated = await service.update_user(
        user.id,
        UserUpdate(full_name="New Name")
    )

    assert updated.full_name == "New Name"


@pytest.mark.asyncio
async def test_change_password(service):
    user = await service.create_user(
        UserCreate(
            email="pwd@mail.com",
            password="oldpass",
            full_name="User",
        )
    )

    result = await service.change_password(
        user.id,
        "oldpass",
        "newpass",
    )

    assert result["message"] == "Password updated"


@pytest.mark.asyncio
async def test_change_password_invalid(service):
    user = await service.create_user(
        UserCreate(
            email="wrong@mail.com",
            password="correct",
            full_name="User",
        )
    )

    with pytest.raises(InvalidPassword):
        await service.change_password(
            user.id,
            "wrong",
            "newpass",
        )


@pytest.mark.asyncio
async def test_get_users_by_ids(service):
    u1 = await service.create_user(
        UserCreate(email="a@mail.com", password="1", full_name="A")
    )
    u2 = await service.create_user(
        UserCreate(email="b@mail.com", password="1", full_name="B")
    )

    users = await service.get_users_by_ids([u1.id, u2.id])

    assert len(users) == 2
