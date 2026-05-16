"""HTTP эндпоинты для аутентификации."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.dependencies.auth import get_current_user
from app.models import Person
from app.core.security import verify_password, create_access_token
from app.crud import person as person_crud
from app.schemas.auth import Token, LoginRequest, AuthUserRead

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Авторизация пользователя.

    Возвращает JWT-токен для использования в заголовке `Authorization: Bearer <token>`.
    """
    user = person_crud.get_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )

    # Собираем роли пользователя для токена
    roles = [r.role.role_name for r in user.system_roles]

    token = create_access_token(data={"sub": user.id, "roles": roles})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=AuthUserRead)
def me(current_user: Person = Depends(get_current_user)):
    """Получить информацию о текущем авторизованном пользователе."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "roles": [r.role.role_name for r in current_user.system_roles],
    }