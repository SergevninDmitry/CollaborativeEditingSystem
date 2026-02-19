import pytest
import respx
from httpx import Response
import httpx
from infrastructure.clients.http_user_client import HttpUserClient
from config import settings



@pytest.mark.asyncio
async def test_get_user_by_email_success():
    email = "test@mail.com"

    url = f"{settings.USER_SERVICE_URL}/users/internal/auth-data"

    with respx.mock(assert_all_mocked=True) as router:
        router.get(
            url,
            params={"email": email},
        ).mock(
            return_value=Response(
                200,
                json={
                    "id": "11111111-1111-1111-1111-111111111111",
                    "email": email,
                    "password": "hashed",
                },
            )
        )

        client = HttpUserClient()

        result = await client.get_user_by_email(email)

        assert result["email"] == email


@pytest.mark.asyncio
async def test_get_user_by_email_not_found():
    email = "missing@mail.com"

    url = f"{settings.USER_SERVICE_URL}/users/internal/auth-data"

    with respx.mock(assert_all_mocked=True) as router:
        router.get(url).mock(
            return_value=Response(404)
        )

        client = HttpUserClient()

        result = await client.get_user_by_email(email)

        assert result is None


@pytest.mark.asyncio
async def test_get_user_by_email_service_error():
    email = "test@mail.com"
    url = f"{settings.USER_SERVICE_URL}/users/internal/auth-data"

    with respx.mock(assert_all_mocked=True) as router:
        router.get(
            url,
            params={"email": email},
        ).mock(
            return_value=Response(500, text="boom")
        )

        client = HttpUserClient()

        with pytest.raises(Exception):
            await client.get_user_by_email(email)



@pytest.mark.asyncio
async def test_get_user_by_email_sends_correct_request():
    email = "test@mail.com"

    url = f"{settings.USER_SERVICE_URL}/users/internal/auth-data"

    with respx.mock(assert_all_mocked=True) as router:
        route = router.get(url).mock(
            return_value=Response(
                200,
                json={
                    "id": "1",
                    "email": email,
                    "password": "hashed",
                },
            )
        )

        client = HttpUserClient()

        await client.get_user_by_email(email)

        request = route.calls[0].request

        assert request.headers["x-service-token"] == settings.INTERNAL_SERVICE_TOKEN
        assert request.url.params["email"] == email
