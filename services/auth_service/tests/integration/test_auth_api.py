import pytest


@pytest.mark.asyncio
async def test_login_success(client, override_auth_service):
    override_auth_service(False)

    response = await client.post(
        "/auth/login",
        json={
            "email": "test@mail.com",
            "password": "123",
        },
    )

    assert response.status_code == 200
    assert response.json()["access_token"] == "fake-token"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client, override_auth_service):
    override_auth_service(True)

    response = await client.post(
        "/auth/login",
        json={
            "email": "bad@mail.com",
            "password": "wrong",
        },
    )

    assert response.status_code == 401
