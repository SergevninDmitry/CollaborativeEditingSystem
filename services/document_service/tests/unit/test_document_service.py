import pytest
from uuid import uuid4

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.pool import StaticPool
from fastapi import HTTPException
from infrastructure.db.base import Base
from infrastructure.db.models.document import Document
from infrastructure.db.models.document_share import DocumentShare

from application.services.document_service import (
    DocumentService,
    DocumentNotFound,
)

from shared.common.schemas.document import DocumentCreate

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


class FakeVersionClient:

    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        self.called = False

    async def create_initial_version(
            self,
            document_id,
            content,
            user_id,
            token,
    ):
        self.called = True

        if self.should_fail:
            raise Exception("version service error")

        return {"ok": True}


@pytest.fixture()
async def service(session):
    return DocumentService(session, FakeVersionClient())


@pytest.mark.asyncio
async def test_create_document_success(session):
    fake_client = FakeVersionClient()
    service = DocumentService(session, fake_client)

    owner = uuid4()

    doc = await service.create_document(
        DocumentCreate(title="Doc", content="Hello"),
        owner,
        token="fake",
    )

    assert doc.title == "Doc"
    assert doc.owner_id == owner
    assert fake_client.called is True


@pytest.mark.asyncio
async def test_create_document_version_failure(session):

    fake_client = FakeVersionClient(should_fail=True)
    service = DocumentService(session, fake_client)

    with pytest.raises(HTTPException) as exc:
        await service.create_document(
            DocumentCreate(title="Fail", content="X"),
            uuid4(),
            token="fake",
        )

    assert exc.value.status_code == 500
    assert fake_client.called is True



@pytest.mark.asyncio
async def test_get_document_success(service, session):
    owner = uuid4()

    doc = Document(title="Doc", owner_id=owner)
    session.add(doc)
    await session.commit()

    fetched = await service.get_document(doc.id)

    assert fetched.id == doc.id


@pytest.mark.asyncio
async def test_get_document_not_found(service):
    with pytest.raises(DocumentNotFound):
        await service.get_document(uuid4())


@pytest.mark.asyncio
async def test_get_documents_owned(service, session):
    user_id = uuid4()

    doc = Document(title="Owned", owner_id=user_id)
    session.add(doc)
    await session.commit()

    docs = await service.get_documents(user_id)

    assert len(docs) == 1
    assert docs[0].title == "Owned"


@pytest.mark.asyncio
async def test_get_documents_shared(service, session):
    owner = uuid4()
    shared_user = uuid4()

    doc = Document(title="Shared", owner_id=owner)
    session.add(doc)
    await session.flush()

    share = DocumentShare(
        document_id=doc.id,
        user_id=shared_user,
    )
    session.add(share)
    await session.commit()

    docs = await service.get_documents(shared_user)

    assert len(docs) == 1
    assert docs[0].title == "Shared"


@pytest.mark.asyncio
async def test_share_document_success(service, session):
    owner = uuid4()
    target = uuid4()

    doc = Document(title="Doc", owner_id=owner)
    session.add(doc)
    await session.commit()

    result = await service.share_document(
        doc.id,
        owner,
        target,
    )

    assert result["message"] == "Document shared successfully"


@pytest.mark.asyncio
async def test_share_document_duplicate(service, session):
    owner = uuid4()
    target = uuid4()

    doc = Document(title="Doc", owner_id=owner)
    session.add(doc)
    await session.flush()

    session.add(DocumentShare(
        document_id=doc.id,
        user_id=target
    ))
    await session.commit()

    result = await service.share_document(
        doc.id,
        owner,
        target,
    )

    assert result["message"] == "Already shared"


@pytest.mark.asyncio
async def test_share_document_forbidden(service, session):
    owner = uuid4()
    stranger = uuid4()

    doc = Document(title="Doc", owner_id=owner)
    session.add(doc)
    await session.commit()

    with pytest.raises(Exception):
        await service.share_document(
            doc.id,
            stranger,
            uuid4(),
        )
