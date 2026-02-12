from dataclasses import dataclass
from dotenv import load_dotenv, find_dotenv
import os
import logging

load_dotenv(find_dotenv())


@dataclass
class Settings:
    HOST: str = os.environ.get("HOST")
    PORT: int = int(os.environ.get("FAST_API_PORT", 8000))
    DATABASE_URL: str = os.environ.get(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./app.db"
    )


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler()]
    )


settings = Settings()
