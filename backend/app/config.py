from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parents[2] / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    cognodb_uri: str = "bolt://localhost:7687"
    cognodb_user: str = "cognodb"
    cognodb_password: str = "change-me"
    cognodb_database: str = "neo4j"
    api_port: int = 8000
    frontend_origin: str = "http://localhost:5173"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
