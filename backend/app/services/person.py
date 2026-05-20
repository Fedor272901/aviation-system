"""Сервисный слой для сущностей Person."""

from sqlalchemy.orm import Session
from app.crud import person as person_crud
from app.models import Person
from app.schemas.person import PersonCreate, PersonUpdate
from app.auth.hashing import verify_password
import logging

logger = logging.getLogger(__name__)


class PersonService:
    """Сервис для работы с пользователями."""

    def __init__(self, db: Session):
        self.db = db

    def create_person(self, payload: PersonCreate) -> Person:
        """Создать пользователя с проверкой уникальности."""
        if person_crud.get_by_email(self.db, payload.email):
            raise ValueError("Email уже зарегистрирован")
        if person_crud.get_by_passport(self.db, payload.passport):
            raise ValueError("Паспорт уже зарегистрирован")

        return person_crud.create_person(self.db, payload)

    def get_person(self, person_id: int) -> Person | None:
        """Получить пользователя по ID."""
        return person_crud.get_person(self.db, person_id)

    def update_person(self, person_id: int, payload: PersonUpdate) -> Person:
        """Обновить пользователя с проверкой уникальности."""
        person = person_crud.get_person(self.db, person_id)
        if not person:
            raise ValueError("Пользователь не найден")

        update_data = payload.model_dump(exclude_unset=True)

        if "email" in update_data and update_data["email"] != person.email:
            if person_crud.get_by_email(self.db, update_data["email"]):
                raise ValueError("Email уже занят")

        if "passport" in update_data and update_data["passport"] != person.passport:
            if person_crud.get_by_passport(self.db, update_data["passport"]):
                raise ValueError("Паспорт уже занят")

        return person_crud.update_person(self.db, person, payload)

    def delete_person(self, person_id: int) -> dict:
        """Удалить пользователя."""
        person = person_crud.get_person(self.db, person_id)
        if not person:
            raise ValueError("Пользователь не найден")

        return person_crud.delete_person(self.db, person)

    def change_password(
        self, person_id: int, old_password: str, new_password: str
    ) -> Person:
        """Сменить пароль с проверкой старого."""
        person = person_crud.get_person(self.db, person_id)
        if not person:
            raise ValueError("Пользователь не найден")

        if not verify_password(old_password, person.password_hash):
            raise ValueError("Неверный текущий пароль")

        return person_crud.change_password(self.db, person, new_password)

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Person]:
        """Получить всех пользователей с пагинацией."""
        return person_crud.get_all(self.db, skip, limit)