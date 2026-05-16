from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List
from pydantic import ConfigDict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24

    # Application
    DEBUG: bool = False
    APP_NAME: str = "Aviation System"
    VERSION: str = "1.0.0"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
    )


@lru_cache()
def get_settings() -> Settings:
    """Возвращает кэшированный объект настроек."""
    return Settings()