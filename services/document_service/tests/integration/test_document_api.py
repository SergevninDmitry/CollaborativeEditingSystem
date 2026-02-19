import pytest
from uuid import uuid4


@pytest.mark.asyncio
async def test_create_document(client, override_current_user):
    user_id = uuid4()
    override_current_user(user_id)

    response = await client.post(
        "/documents/",
        json={
            "title": "Test doc",
            "content": "Hello",
        },
        headers={"Authorization": "Bearer fake"},
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Test doc"


@pytest.mark.asyncio
async def test_get_documents(client, override_current_user):
    user_id = uuid4()
    override_current_user(user_id)

    await client.post(
        "/documents/",
        json={"title": "Doc1", "content": "A"},
        headers={"Authorization": "Bearer fake"},
    )

    response = await client.get("/documents/")

    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_get_document_forbidden(client, override_current_user):
    owner = uuid4()
    override_current_user(owner)

    create = await client.post(
        "/documents/",
        json={"title": "Doc", "content": "A"},
        headers={"Authorization": "Bearer fake"},
    )

    doc_id = create.json()["id"]

    # другой пользователь
    override_current_user(uuid4())

    response = await client.get(f"/documents/{doc_id}")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_share_document(client, override_current_user):
    owner = uuid4()
    override_current_user(owner)

    create = await client.post(
        "/documents/",
        json={"title": "Doc", "content": "A"},
        headers={"Authorization": "Bearer fake"},
    )

    doc_id = create.json()["id"]

    response = await client.post(
        f"/documents/{doc_id}/share",
        json={"email": "user@test.com"},
    )

    assert response.status_code == 200
