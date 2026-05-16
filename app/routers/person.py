from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.person import PersonService
from app.utils.api_utils import raise_from_value_error
from app.schemas.person import (
    PersonRead,
    PersonCreate,
    PersonUpdate,
    PasswordChange,
    DeleteResponse,
)

router = APIRouter(prefix="/persons", tags=["Пользователи"])


@router.get("/", response_model=list[PersonRead], summary="Получить всех пользователей")
def list_persons(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получить список пользователей с пагинацией."""
    service = PersonService(db)
    return service.get_all(skip=skip, limit=limit)


@router.get(
    "/{person_id}",
    response_model=PersonRead,
    summary="Получить конкретного пользователя",
)
def get_person(person_id: int, db: Session = Depends(get_db)):
    """Получить пользователя по ID."""
    service = PersonService(db)
    person = service.get_person(person_id)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
        )
    return person


@router.post(
    "/",
    response_model=PersonRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать пользователя",
)
def create_person(payload: PersonCreate, db: Session = Depends(get_db)):
    """Создать нового пользователя."""
    service = PersonService(db)
    try:
        return service.create_person(payload)
    except ValueError as e:
        raise_from_value_error(e)


@router.put(
    "/{person_id}",
    response_model=PersonRead,
    summary="Обновить информацию о пользователе",
)
def update_person(person_id: int, payload: PersonUpdate, db: Session = Depends(get_db)):
    """Обновить данные пользователя (без пароля)."""
    service = PersonService(db)
    try:
        return service.update_person(person_id, payload)
    except ValueError as e:
        raise_from_value_error(e)


@router.put(
    "/{person_id}/password",
    response_model=PersonRead,
    summary="Сменить пароль пользователя",
)
def change_password(
    person_id: int,
    payload: PasswordChange,
    db: Session = Depends(get_db),
):
    """
    Сменить пароль пользователя.

    Требуется предоставить текущий пароль для проверки.
    """
    service = PersonService(db)
    try:
        return service.change_password(person_id, payload.old_password, payload.new_password)
    except ValueError as e:
        raise_from_value_error(e)


@router.delete(
    "/{person_id}", response_model=DeleteResponse, summary="Удалить пользователя"
)
def delete_person(person_id: int, db: Session = Depends(get_db)):
    """Удалить пользователя."""
    service = PersonService(db)
    try:
        return service.delete_person(person_id)
    except ValueError as e:
        raise_from_value_error(e)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении: {str(e)}")
