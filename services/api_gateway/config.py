import os
from dataclasses import dataclass


@dataclass
class Settings:
    AUTH_SERVICE_URL: str = os.getenv(
        "AUTH_SERVICE_URL",
        "http://auth_service:8004"
    )

    USER_SERVICE_URL: str = os.getenv(
        "USER_SERVICE_URL",
        "http://user_service:8003"
    )

    DOCUMENT_SERVICE_URL: str = os.getenv(
        "DOCUMENT_SERVICE_URL",
        "http://document_service:8002"
    )

    VERSION_SERVICE_URL: str = os.getenv(
        "VERSION_SERVICE_URL",
        "http://version_service:8001"
    )


settings = Settings()
