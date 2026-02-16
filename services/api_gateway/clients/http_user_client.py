import httpx
from config import settings

class UserClient:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=settings.USER_SERVICE_URL)

    async def register(self, data: dict):
        response = await self.client.post("/users", json=data)
        return response

    async def get_me(self, token: str):
        response = await self.client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
        return response

    async def update_me(self, token: str, data: dict):
        response = await self.client.put("/users/me", json=data, headers={"Authorization": f"Bearer {token}"})
        return response

    async def change_password(self, token: str, data: dict):
        response = await self.client.post("/users/me/change-password", json=data, headers={"Authorization": f"Bearer {token}"})
        return response

    async def get_user(self, token: str, user_id: str):
        response = await self.client.post(f"/users/{user_id}", headers={"Authorization": f"Bearer {token}"})
        return response
