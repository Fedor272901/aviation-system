from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from typing import Optional

class PersonBase(BaseModel):
    first_name: str = Field(..., max_length=30)
    last_name: str = Field(..., max_length=30)
    middle_name: Optional[str] = Field(None, max_length=30)
    phone: Optional[str] = Field(None, max_length=20)
    passport: str = Field(..., max_length=15)
    email: EmailStr


class PersonCreate(PersonBase):
    password: str = Field(..., min_length=6, max_length=72)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Пароль должен быть не менее 6 символов")
        if not any(c.isupper() for c in v):
            raise ValueError("Пароль должен содержать хотя одну заглавную букву")
        if not any(c.isdigit() for c in v):
            raise ValueError("Пароль должен содержать хотя одну цифру")
        return v


class PersonUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=30)
    last_name: Optional[str] = Field(None, max_length=30)
    middle_name: Optional[str] = Field(None, max_length=30)
    phone: Optional[str] = Field(None, max_length=20)
    passport: Optional[str] = Field(None, max_length=15)
    email: Optional[EmailStr] = None


class PasswordChange(BaseModel):
    """Схема для смены пароля."""

    old_password: str = Field(..., description="Текущий пароль")
    new_password: str = Field(
        ..., min_length=6, max_length=72, description="Новый пароль"
    )

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Пароль должен быть не менее 6 символов")
        if not any(c.isupper() for c in v):
            raise ValueError("Пароль должен содержать хотя одну заглавную букву")
        if not any(c.isdigit() for c in v):
            raise ValueError("Пароль должен содержать хотя одну цифру")
        return v


class PersonRead(PersonBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class DeleteResponse(BaseModel):
    """Ответ при успешном удалении."""

    message: str
    deleted_id: int
