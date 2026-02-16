from dataclasses import dataclass
from dotenv import load_dotenv, find_dotenv
import os
import logging

load_dotenv(find_dotenv())


@dataclass
class Settings:
    HOST: str = os.environ.get("HOST")
    FASTAPI_PORT: int = int(os.environ.get("FASTAPI_PORT", 8000))
    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = os.environ.get("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
    USER_SERVICE_URL: str = os.getenv("USER_SERVICE_URL", "http://user_service:8003")


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler()]
    )


settings = Settings()
