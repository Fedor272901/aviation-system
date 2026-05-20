from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List
from pydantic import ConfigDict, field_validator
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    DB_PASSWORD: str | None = None  # ← Добавить это поле

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24

    # Application
    DEBUG: bool = False
    APP_NAME: str = "Aviation System"
    VERSION: str = "1.0.0"

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:80",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:80",
    ]
    model_config = ConfigDict(
        env_file=BASE_DIR / ".env",
        case_sensitive=True,
    )

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError(
                "SECRET_KEY должен быть не менее 32 символов. "
                "Сгенерируйте: openssl rand -hex 32"
            )
        return v


@lru_cache()
def get_settings() -> Settings:
    """Возвращает кэшированный объект настроек."""
    return Settings()
