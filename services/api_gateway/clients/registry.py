from clients.http_auth_client import AuthClient
from clients.http_user_client import UserClient
from clients.http_document_client import DocumentClient
from clients.http_version_client import VersionClient


class Clients:
    def __init__(self):
        self.auth = AuthClient()
        self.user = UserClient()
        self.documents = DocumentClient()
        self.versions = VersionClient()

    async def close(self):
        await self.auth.close()
        await self.user.close()
        await self.documents.close()
        await self.versions.close()
