"""HTTP эндпоинты для аутентификации."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.dependencies.auth import get_current_user
from app.core.security import verify_password, create_access_token
from app.crud import person as person_crud
from app.schemas.auth import Token, LoginRequest, AuthUserRead
from app.schemas.person import PersonCreate
from app.models import Person

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=AuthUserRead)
def register(payload: PersonCreate, db: Session = Depends(get_db)):
    """
    Регистрация нового пользователя.

    Создаёт пользователя с ролью "user" по умолчанию.
    """
    # Проверка на дубликат email
    existing = person_crud.get_by_email(db, payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email уже зарегистрирован",
        )

    # Проверка на дубликат паспорта
    if payload.passport:
        existing_passport = person_crud.get_by_passport(db, payload.passport)
        if existing_passport:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Паспорт уже зарегистрирован",
            )

    # Создаём пользователя
    user = person_crud.create_person(db, payload)

    # Проверяем, есть ли роль "user"
    user_role = person_crud.get_role_by_name(db, "user")
    if not user_role:
        # Создаём роль "user" если её нет
        from app.models import SystemRole

        user_role = SystemRole(role_name="user")
        db.add(user_role)
        db.commit()
        db.refresh(user_role)

    # Назначаем роль пользователю
    from app.models import PeopleSystemRole

    role_assignment = PeopleSystemRole(person_id=user.id, role_id=user_role.id)
    db.add(role_assignment)
    db.commit()

    # Возвращаем данные пользователя
    db.refresh(user)
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "middle_name": user.middle_name,
        "phone": user.phone,
        "passport": user.passport,
        "roles": ["user"],
    }


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

    token = create_access_token(data={"sub": str(user.id), "roles": roles})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=AuthUserRead)
def me(current_user: Person = Depends(get_current_user)):
    """Получить информацию о текущем авторизованном пользователе."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "middle_name": current_user.middle_name,
        "phone": current_user.phone,
        "passport": current_user.passport,
        "roles": [r.role.role_name for r in current_user.system_roles],
    }
