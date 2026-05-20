"""Тесты для сервисного слоя Person."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.models.base import Base
from backend.app.services.person import PersonService
from backend.app.schemas.person import PersonCreate, PersonUpdate
from backend.app.crud import person as person_crud


@pytest.fixture
def test_db():
    """Создаёт тестовую БД."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)

    SessionTest = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionTest()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def person_service(test_db):
    """Создаёт сервис Person."""
    return PersonService(test_db)


@pytest.fixture
def test_person_data():
    """Тестовые данные."""
    return {
        "first_name": "Иван",
        "last_name": "Иванов",
        "middle_name": "Иванович",
        "phone": "+79001234567",
        "passport": "1234567890",
        "email": "ivan@example.com",
        "password": "Test1234!",
    }


class TestPersonServiceCreate:
    """Тесты для создания пользователя."""

    def test_create_person_success(self, person_service, test_person_data):
        """Успешное создание пользователя."""
        payload = PersonCreate(**test_person_data)
        person = person_service.create_person(payload)

        assert person is not None
        assert person.email == test_person_data["email"]
        assert person.first_name == test_person_data["first_name"]
        assert person.last_name == test_person_data["last_name"]
        assert person.password_hash is not None
        assert person.password_hash != test_person_data["password"]

    def test_create_person_duplicate_email(self, person_service, test_person_data):
        """Создание пользователя с дублирующимся email."""
        payload = PersonCreate(**test_person_data)
        person_service.create_person(payload)

        with pytest.raises(ValueError, match="Email уже зарегистрирован"):
            person_service.create_person(payload)

    def test_create_person_duplicate_passport(self, person_service, test_person_data):
        """Создание пользователя с дублирующимся паспортом."""
        payload1 = PersonCreate(**test_person_data)
        payload2 = PersonCreate(**test_person_data)
        payload2.email = "different@example.com"

        person_service.create_person(payload1)

        with pytest.raises(ValueError, match="Паспорт уже зарегистрирован"):
            person_service.create_person(payload2)


class TestPersonServiceGet:
    """Тесты для получения пользователя."""

    def test_get_person_success(self, person_service, test_db, test_person_data):
        """Успешное получение пользователя."""
        payload = PersonCreate(**test_person_data)
        created = person_service.create_person(payload)

        retrieved = person_service.get_person(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.email == created.email

    def test_get_person_not_found(self, person_service):
        """Получение несуществующего пользователя."""
        result = person_service.get_person(9999)
        assert result is None


class TestPersonServiceUpdate:
    """Тесты для обновления пользователя."""

    def test_update_person_success(self, person_service, test_db, test_person_data):
        """Успешное обновление пользователя."""
        payload = PersonCreate(**test_person_data)
        created = person_service.create_person(payload)

        update_payload = PersonUpdate(first_name="Петр")
        updated = person_service.update_person(created.id, update_payload)

        assert updated.first_name == "Петр"
        assert updated.last_name == test_person_data["last_name"]

    def test_update_person_not_found(self, person_service, test_person_data):
        """Обновление несуществующего пользователя."""
        payload = PersonCreate(**test_person_data)
        person_service.create_person(payload)

        update_payload = PersonUpdate(first_name="Петр")

        with pytest.raises(ValueError, match="Пользователь не найден"):
            person_service.update_person(9999, update_payload)

    def test_update_person_duplicate_email(
        self, person_service, test_db, test_person_data
    ):
        """Обновление с дублирующимся email."""
        payload1 = PersonCreate(**test_person_data)
        payload2 = PersonCreate(**test_person_data)
        payload2.email = "another@example.com"
        payload2.passport = "0987654321"  # Уникальный паспорт

        person1 = person_service.create_person(payload1)
        person_service.create_person(payload2)

        update_payload = PersonUpdate(email="another@example.com")

        with pytest.raises(ValueError, match="Email уже"):
            person_service.update_person(person1.id, update_payload)


class TestPersonServiceDelete:
    """Тесты для удаления пользователя."""

    def test_delete_person_success(self, person_service, test_db, test_person_data):
        """Успешное удаление пользователя."""
        payload = PersonCreate(**test_person_data)
        created = person_service.create_person(payload)

        result = person_service.delete_person(created.id)

        assert result["message"] == "Пользователь успешно удален"
        assert result["deleted_id"] == created.id

        deleted = person_service.get_person(created.id)
        assert deleted is None

    def test_delete_person_not_found(self, person_service):
        """Удаление несуществующего пользователя."""
        with pytest.raises(ValueError, match="Пользователь не найден"):
            person_service.delete_person(9999)


class TestPersonServicePassword:
    """Тесты для смены пароля."""

    def test_change_password_success(self, person_service, test_db, test_person_data):
        """Успешная смена пароля."""
        from backend.app.auth.hashing import verify_password

        payload = PersonCreate(**test_person_data)
        created = person_service.create_person(payload)

        result = person_service.change_password(created.id, "Test1234!", "NewPass123!")

        assert result is not None
        assert verify_password("NewPass123!", result.password_hash)
        assert not verify_password("Test1234!", result.password_hash)

    def test_change_password_wrong_old(self, person_service, test_db, test_person_data):
        """Смена пароля с неверным стартым паролем."""
        payload = PersonCreate(**test_person_data)
        created = person_service.create_person(payload)

        with pytest.raises(ValueError, match="Неверный текущий пароль"):
            person_service.change_password(created.id, "WrongPassword", "NewPass123!")

    def test_change_password_not_found(self, person_service):
        """Смена пароля несуществующего пользователя."""
        with pytest.raises(ValueError, match="Пользователь не найден"):
            person_service.change_password(9999, "OldPass", "NewPass")


class TestPersonServiceGetAll:
    """Тесты для получения всех пользователей."""

    def test_get_all_empty(self, person_service):
        """Получение всех пользователей (пустой список)."""
        result = person_service.get_all()
        assert result == []

    def test_get_all_with_users(self, person_service, test_db, test_person_data):
        """Получение всех пользователей (с пользователями)."""
        for i in range(3):
            data = test_person_data.copy()
            data["email"] = f"user{i}@example.com"
            data["passport"] = f"PASS{i}123456"  # Уникальный паспорт
            payload = PersonCreate(**data)
            person_service.create_person(payload)

        result = person_service.get_all()

        assert len(result) == 3

    def test_get_all_pagination(self, person_service, test_db, test_person_data):
        """Пагинация пользователей."""
        for i in range(5):
            data = test_person_data.copy()
            data["email"] = f"pag{i}@example.com"
            data["passport"] = f"PAG{i}123456"  # Уникальный паспорт
            payload = PersonCreate(**data)
            person_service.create_person(payload)

        result = person_service.get_all(skip=2, limit=2)

        assert len(result) == 2
