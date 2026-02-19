from uuid import uuid4


class FakeVersionClient:

    async def create_initial_version(
        self,
        document_id,
        content,
        user_id,
        token,
    ):
        return {
            "id": "fake-version",
            "content": content,
        }


class FakeUserClient:

    async def get_user_by_email(self, email: str):
        return {
            "id": str(uuid4()),
            "email": email,
        }
