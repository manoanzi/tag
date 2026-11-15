import os

from pydantic import BaseModel, ConfigDict


class Settings(BaseModel):
    model_config = ConfigDict(frozen=True)

    database_path: str = "users.db"
    http_port: int = 8000


def load_settings() -> Settings:
    return Settings(
        database_path=os.getenv("DATABASE_PATH", "users.db"),
        http_port=int(os.getenv("HTTP_PORT", "8000")),
    )
