from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app import crud
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
    return crud.person.get_all(db, skip=skip, limit=limit)


@router.get(
    "/{person_id}",
    response_model=PersonRead,
    summary="Получить конкретного пользователя",
)
def get_person(person_id: int, db: Session = Depends(get_db)):
    """Получить пользователя по ID."""
    person = crud.person.get_person(db, person_id)
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
    try:
        return crud.person.create_person(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/{person_id}",
    response_model=PersonRead,
    summary="Обновить информацию о  пользователе",
)
def update_person(person_id: int, payload: PersonUpdate, db: Session = Depends(get_db)):
    """Обновить данные пользователя (без пароля)."""
    person = crud.person.get_person(db, person_id)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
        )

    try:
        return crud.person.update_person(db, person, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


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
    person = crud.person.get_person(db, person_id)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
        )

    try:
        return crud.person.change_password(
            db, person, payload.old_password, payload.new_password
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/{person_id}", response_model=DeleteResponse, summary="Удалить пользователя"
)
def delete_person(person_id: int, db: Session = Depends(get_db)):
    """Удалить пользователя."""
    person = crud.person.get_person(db, person_id)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
        )

    try:
        return crud.person.delete_person(db, person)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении: {str(e)}")
