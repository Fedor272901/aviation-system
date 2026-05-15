from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import Person
from app.schemas.person import PersonCreate, PersonUpdate
from app.auth.hashing import hash_password, verify_password
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
    """Создать нового пользователя."""
    # Проверка на существование
    if get_by_email(db, payload.email):
        raise ValueError("Email уже зарегистрирован")
    if get_by_passport(db, payload.passport):
        raise ValueError("Паспорт уже зарегистрирован")

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
    """Обновить данные пользователя (без пароля)."""

    update_data = payload.model_dump(exclude_unset=True)

    # Проверка на занятость email/passport другими пользователями
    if update_data.get("email") and update_data["email"] != person.email:
        if get_by_email(db, update_data["email"]):
            raise ValueError("Email уже занят")

    if update_data.get("passport") and update_data["passport"] != person.passport:
        if get_by_passport(db, update_data["passport"]):
            raise ValueError("Паспорт уже занят")

    # Обновляем поля
    for field, value in update_data.items():
        setattr(person, field, value)

    db.commit()
    db.refresh(person)

    logger.info(f"Обновлен пользователь: {person.email} (id={person.id})")
    return person


def change_password(
    db: Session, person: Person, old_password: str, new_password: str
) -> Person:
    """Сменить пароль с проверкой старого."""
    # Проверка старого пароля
    if not verify_password(old_password, person.password_hash):
        raise ValueError("Неверный текущий пароль")

    # Обновление пароля
    person.password_hash = hash_password(new_password)
    db.commit()
    db.refresh(person)

    logger.info(f"Пароль обновлён для пользователя: {person.email} (id={person.id})")
    return person


def delete_person(db: Session, person: Person) -> dict:
    """Удалить пользователя."""
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
