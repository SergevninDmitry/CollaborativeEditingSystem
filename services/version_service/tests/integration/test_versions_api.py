import pytest
from dependencies import get_version_service
from application.versions.version_service import DocumentVersionService
from main import app


class FakeUserClient:

    async def get_users_batch(self, user_ids):
        return {uid: "test@example.com" for uid in user_ids}

    async def get_user_email(self, user_id):
        return "test@example.com"



@pytest.fixture(autouse=True)
async def override_version_service(db_session):

    fake_user_client = FakeUserClient()

    async def _service_override():
        yield DocumentVersionService(
            db_session,
            fake_user_client,
        )

    app.dependency_overrides[get_version_service] = _service_override

    yield

    app.dependency_overrides.pop(get_version_service, None)


import pytest
from uuid import uuid4


@pytest.mark.asyncio
async def test_create_version(client):

    document_id = uuid4()

    response = await client.post(
        f"/versions/{document_id}/versions",
        json={
            "content": "Hello world",
            "base_version_id": None,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["document_id"] == str(document_id)
    assert data["content"] == "Hello world"




@pytest.mark.asyncio
async def test_get_versions(client):

    document_id = uuid4()

    await client.post(
        f"/versions/{document_id}/versions",
        json={"content": "v1", "base_version_id": None},
    )

    response = await client.get(
        f"/versions/{document_id}/versions"
    )

    assert response.status_code == 200

    versions = response.json()

    assert len(versions) == 1
    assert versions[0]["content"] == "v1"



@pytest.mark.asyncio
async def test_version_conflict(client):

    document_id = uuid4()

    r1 = await client.post(
        f"/versions/{document_id}/versions",
        json={"content": "v1", "base_version_id": None},
    )

    first_version = r1.json()["id"]

    await client.post(
        f"/versions/{document_id}/versions",
        json={"content": "v2", "base_version_id": first_version},
    )

    conflict = await client.post(
        f"/versions/{document_id}/versions",
        json={"content": "v3", "base_version_id": first_version},
    )

    assert conflict.status_code == 409


@pytest.mark.asyncio
async def test_revert_version(client):

    document_id = uuid4()

    r1 = await client.post(
        f"/versions/{document_id}/versions",
        json={"content": "original", "base_version_id": None},
    )

    version_id = r1.json()["id"]

    response = await client.post(
        f"/versions/{document_id}/revert/{version_id}"
    )

    assert response.status_code == 200
    assert response.json()["content"] == "original"


@pytest.mark.asyncio
async def test_get_diff(client):

    document_id = uuid4()

    await client.post(
        f"/versions/{document_id}/versions",
        json={"content": "line1", "base_version_id": None},
    )

    r2 = await client.post(
        f"/versions/{document_id}/versions",
        json={"content": "line1\nline2", "base_version_id": None},
    )

    version_id = r2.json()["id"]

    response = await client.get(
        f"/versions/{document_id}/diff/{version_id}"
    )

    assert response.status_code == 200
    assert "diff" in response.json()


