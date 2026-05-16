"""Схемы Pydantic для аутентификации."""

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """Ответ с JWT токеном."""

    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    """Запрос на вход."""

    email: EmailStr
    password: str


class AuthUserRead(BaseModel):
    """Текущий пользователь (из токена)."""

    id: int
    email: str
    first_name: str
    last_name: str
    roles: list[str]

    model_config = {"from_attributes": True}