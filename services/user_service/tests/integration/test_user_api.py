import pytest
from uuid import UUID


@pytest.mark.asyncio
async def test_create_user(client):
    response = await client.post(
        "/users/",
        json={
            "email": "api@test.com",
            "password": "123456",
            "full_name": "API User"
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["email"] == "api@test.com"


@pytest.mark.asyncio
async def test_duplicate_email(client):
    payload = {
        "email": "dup@test.com",
        "password": "123",
        "full_name": "User"
    }

    await client.post("/users/", json=payload)

    response = await client.post("/users/", json=payload)

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_get_user(client):
    create = await client.post(
        "/users/",
        json={
            "email": "get@test.com",
            "password": "123",
            "full_name": "User"
        },
    )

    user_id = create.json()["id"]

    response = await client.get(f"/users/{user_id}")

    assert response.status_code == 200
    assert response.json()["id"] == user_id


@pytest.mark.asyncio
async def test_update_user(client, override_current_user):
    create = await client.post(
        "/users/",
        json={
            "email": "update@test.com",
            "password": "123",
            "full_name": "Old"
        },
    )

    user_id = UUID(create.json()["id"])

    override_current_user(user_id)

    response = await client.put(
        "/users/me",
        json={"full_name": "New Name"},
    )

    assert response.status_code == 200

@pytest.mark.asyncio
async def test_change_password(client, override_current_user):

    create = await client.post(
        "/users/",
        json={
            "email": "pwd@test.com",
            "password": "oldpass",
            "full_name": "User"
        },
    )

    user_id = UUID(create.json()["id"])

    override_current_user(user_id)

    response = await client.post(
        "/users/me/change-password",
        json={
            "old_password": "oldpass",
            "new_password": "newpass"
        },
    )

    assert response.status_code == 200
