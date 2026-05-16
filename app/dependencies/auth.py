"""Зависимости FastAPI для аутентификации и авторизации."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.security import verify_token
from app.dependencies import get_db
from app.crud import person as person_crud
from app.models import Person

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> Person:
    """Получить текущего пользователя из Bearer-токена."""
    token = credentials.credentials
    payload = verify_token(token)
    if not payload or not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или просроченный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = int(payload["sub"])
    user = person_crud.get_person(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
        )
    return user


def get_current_active_user(
    current_user: Person = Depends(get_current_user),
) -> Person:
    """Проверка, что пользователь активен (заготовка на будущее)."""
    return current_user


def require_roles(*role_names: str):
    """Фабрика зависимостей: проверка ролей пользователя.

    Возвращает функцию-чекер, которую нужно оборачивать в Depends() при использовании.
    Пример: Depends(require_roles("admin"))
    """

    def checker(current_user: Person = Depends(get_current_user)) -> Person:
        user_roles = {r.role.role_name for r in current_user.system_roles}
        if not user_roles.intersection(role_names):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Требуется одна из ролей: {', '.join(role_names)}",
            )
        return current_user

    return checker


# Удобные алиасы
require_admin = require_roles("admin")
