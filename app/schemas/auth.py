"""Схемы Pydantic для аутентификации."""

from pydantic import BaseModel, EmailStr
from typing import Optional

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
    middle_name: Optional[str] = None
    phone: Optional[str] = None
    passport: str
    roles: list[str]

    model_config = {"from_attributes": True}
