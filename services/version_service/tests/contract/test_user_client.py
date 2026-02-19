import pytest
from uuid import uuid4
from config import settings

import respx
from httpx import Response
from infrastructure.integrations.http_user_client import HttpUserClient


@pytest.mark.asyncio
async def test_get_user_email_success():
    user_id = uuid4()
    url = f"{settings.USER_SERVICE_URL}/users/{user_id}"

    # ВАЖНО: явный router context
    with respx.mock(assert_all_mocked=True) as router:
        router.get(url).mock(
            return_value=Response(
                200,
                json={"email": "test@example.com"}
            )
        )

        client = HttpUserClient()

        email = await client.get_user_email(user_id)

        assert email == "test@example.com"


@pytest.mark.asyncio
@respx.mock
async def test_get_user_email_fallback_on_error():
    user_id = uuid4()

    respx.get(
        f"{settings.USER_SERVICE_URL}/users/{user_id}"
    ).mock(return_value=Response(404))

    client = HttpUserClient()

    email = await client.get_user_email(user_id)

    assert email == "unknown"


@pytest.mark.asyncio
@respx.mock
async def test_get_users_batch_success():
    user1 = uuid4()
    user2 = uuid4()

    response_json = {
        str(user1): {"id": str(user1), "email": "a@test.com"},
        str(user2): {"id": str(user2), "email": "b@test.com"},
    }

    route = respx.get(
        f"{settings.USER_SERVICE_URL}/users/internal/batch"
    ).mock(return_value=Response(200, json=response_json))

    client = HttpUserClient()

    result = await client.get_users_batch([user1, user2])

    assert result[user1] == "a@test.com"
    assert result[user2] == "b@test.com"
    assert route.called


@pytest.mark.asyncio
async def test_get_users_batch_empty():
    client = HttpUserClient()

    result = await client.get_users_batch([])

    assert result == {}


@pytest.mark.asyncio
async def test_client_close():
    client = HttpUserClient()
    await client.close()
