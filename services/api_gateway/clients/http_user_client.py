import httpx
from config import settings
from uuid import UUID


class UserClient:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=settings.USER_SERVICE_URL)

    async def register(self, data: dict):
        response = await self.client.post("/users/", json=data)
        return response

    async def get_me(self, token: str):
        response = await self.client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
        return response

    async def update_me(self, token: str, data: dict):
        response = await self.client.put("/users/me", json=data, headers={"Authorization": f"Bearer {token}"})
        return response

    async def change_password(self, token: str, data: dict):
        response = await self.client.post("/users/me/change-password", json=data,
                                          headers={"Authorization": f"Bearer {token}"})
        return response

    async def get_user(self, token: str, user_id: str):
        response = await self.client.get(f"/users/{user_id}", headers={"Authorization": f"Bearer {token}"})
        return response

    async def get_users_batch(self, token: str, user_ids: list[str]):
        if not user_ids:
            return {}

        params = [
            ("ids", str(uid))
            for uid in user_ids
        ]

        response = await self.client.get(
            "/users/internal/batch",
            params=params,
            headers={
                "Authorization": f"Bearer {token}",
                "x-service-token": settings.INTERNAL_SERVICE_TOKEN,
            },
        )
        response.raise_for_status()
        data = response.json()
        return {
            UUID(uid): user_data["email"]
            for uid, user_data in data.items()
        }
