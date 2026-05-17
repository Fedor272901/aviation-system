from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import Person, SystemRole
from app.schemas.person import PersonCreate, PersonUpdate
from app.auth.hashing import hash_password
import logging

logger = logging.getLogger(__name__)


def get_person(db: Session, person_id: int) -> Person | None:
    """Получить пользователя по ID."""
    return db.get(Person, person_id)


def get_by_email(db: Session, email: str) -> Person | None:
    """Получить пользователя по email."""
    return db.scalar(select(Person).where(Person.email == email))


def get_by_passport(db: Session, passport: str) -> Person | None:
    """Получить пользователя по паспорту."""
    return db.scalar(select(Person).where(Person.passport == passport))


def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[Person]:
    """Получить всех пользователей с пагинацией."""
    return (
        db.execute(select(Person).order_by(Person.id).offset(skip).limit(limit))
        .scalars()
        .all()
    )


def create_person(db: Session, payload: PersonCreate) -> Person:
    """Создать нового пользователя (без проверок - только INSERT)."""
    person = Person(
        first_name=payload.first_name,
        last_name=payload.last_name,
        middle_name=payload.middle_name,
        phone=payload.phone,
        passport=payload.passport,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )

    db.add(person)
    db.commit()
    db.refresh(person)

    logger.info(f"Создан новый пользователь: {person.email} (id={person.id})")
    return person


def update_person(db: Session, person: Person, payload: PersonUpdate) -> Person:
    """Обновить данные пользователя (без проверок - только UPDATE)."""

    update_data = payload.model_dump(exclude_unset=True)

    if update_data:
        for field, value in update_data.items():
            setattr(person, field, value)

    db.commit()
    db.refresh(person)

    logger.info(f"Обновлен пользователь: {person.email} (id={person.id})")
    return person


def change_password(db: Session, person: Person, new_password: str) -> Person:
    """Сменить пароль (без проверок - только UPDATE)."""
    person.password_hash = hash_password(new_password)
    db.commit()
    db.refresh(person)

    logger.info(f"Пароль обновлён для пользователя: {person.email} (id={person.id})")
    return person


def delete_person(db: Session, person: Person) -> dict:
    """Удалить пользователя (без проверок - только DELETE)."""
    person_id = person.id
    person_email = person.email

    logger.info(f"Удален пользователь: {person_email} (id={person_id})")

    db.delete(person)
    db.commit()

    return {
        "message": "Пользователь успешно удален",
        "deleted_id": person_id,
        "deleted_email": person_email,
    }


def get_role_by_name(db: Session, role_name: str) -> SystemRole | None:
    """Получить роль по имени."""
    return db.scalar(select(SystemRole).where(SystemRole.role_name == role_name))
