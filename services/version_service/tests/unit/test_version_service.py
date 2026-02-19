import pytest
from uuid import uuid4

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.pool import StaticPool

from infrastructure.db.base import Base
from application.versions.version_service import (
    DocumentVersionService,
    VersionConflict,
)


class FakeUserClient:

    async def get_users_batch(self, user_ids):
        return {uid: "unit@test.com" for uid in user_ids}

    async def get_user_email(self, user_id):
        return "unit@test.com"


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
    return DocumentVersionService(
        session,
        FakeUserClient(),
    )


@pytest.mark.asyncio
async def test_add_version(service):
    doc_id = uuid4()
    user_id = uuid4()

    version = await service.add_version(
        doc_id,
        "hello",
        user_id,
        None,
    )

    assert version.content == "hello"
    assert version.document_id == doc_id


@pytest.mark.asyncio
async def test_version_conflict(service):
    doc_id = uuid4()
    user_id = uuid4()

    v1 = await service.add_version(doc_id, "v1", user_id, None)

    await service.add_version(doc_id, "v2", user_id, v1.id)

    with pytest.raises(VersionConflict):
        await service.add_version(doc_id, "v3", user_id, v1.id)


@pytest.mark.asyncio
async def test_get_versions(service):
    doc_id = uuid4()
    user_id = uuid4()

    await service.add_version(doc_id, "v1", user_id, None)

    versions = await service.get_versions(doc_id)

    assert len(versions) == 1
    assert versions[0]["author_email"] == "unit@test.com"


@pytest.mark.asyncio
async def test_revert_version(service):
    doc_id = uuid4()
    user_id = uuid4()

    v1 = await service.add_version(doc_id, "original", user_id, None)

    reverted = await service.revert_to_version(
        doc_id,
        v1.id,
        user_id,
    )

    assert reverted["content"] == "original"


@pytest.mark.asyncio
async def test_get_diff(service):
    doc_id = uuid4()
    user_id = uuid4()

    await service.add_version(doc_id, "line1", user_id, None)

    v2 = await service.add_version(
        doc_id,
        "line1\nline2",
        user_id,
        None,
    )

    diff = await service.get_diff(doc_id, v2.id)

    assert isinstance(diff, str)
