from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.dependencies.auth import get_current_user, require_admin
from app.models import Person
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


def _check_self_or_admin(current_user: Person, target_id: int) -> None:
    """Проверяет, что пользователь обращается к своим данным или является админом."""
    user_roles = {r.role.role_name for r in current_user.system_roles}
    if current_user.id != target_id and "admin" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к данному ресурсу",
        )


@router.get(
    "/",
    response_model=list[PersonRead],
    summary="Получить всех пользователей (только admin)",
)
def list_persons(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Person = Depends(require_admin),
):
    """Получить список пользователей с пагинацией. Только для администраторов."""
    service = PersonService(db)
    return service.get_all(skip=skip, limit=limit)


@router.get(
    "/{person_id}",
    response_model=PersonRead,
    summary="Получить конкретного пользователя",
)
def get_person(
    person_id: int,
    db: Session = Depends(get_db),
    current_user: Person = Depends(get_current_user),
):
    """Получить пользователя по ID. Доступно самому пользователю или админу."""
    _check_self_or_admin(current_user, person_id)

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
def create_person(
    payload: PersonCreate,
    db: Session = Depends(get_db),
    # Примечание: для открытой регистрации уберите Depends(get_current_user)
    current_user: Person = Depends(get_current_user),
):
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
def update_person(
    person_id: int,
    payload: PersonUpdate,
    db: Session = Depends(get_db),
    current_user: Person = Depends(get_current_user),
):
    """Обновить данные пользователя. Доступно самому пользователю или админу."""
    _check_self_or_admin(current_user, person_id)

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
    current_user: Person = Depends(get_current_user),
):
    """
    Сменить пароль пользователя. Доступно только самому пользователю.
    Требуется предоставить текущий пароль для проверки.
    """
    if current_user.id != person_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Можно менять только свой пароль",
        )

    service = PersonService(db)
    try:
        return service.change_password(
            person_id, payload.old_password, payload.new_password
        )
    except ValueError as e:
        raise_from_value_error(e)


@router.delete(
    "/{person_id}", response_model=DeleteResponse, summary="Удалить пользователя"
)
def delete_person(
    person_id: int,
    db: Session = Depends(get_db),
    current_user: Person = Depends(require_admin),
):
    """Удалить пользователя. Только для администраторов."""
    service = PersonService(db)
    try:
        return service.delete_person(person_id)
    except ValueError as e:
        raise_from_value_error(e)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении: {str(e)}")