"""Конфигурация и фикстуры для тестов."""

import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.models.base import Base
from app.main import app
from app.dependencies import get_db


# Тестовая конфигурация
@pytest.fixture(scope="function")
def test_engine():
    """Создаёт тестовую базу данных SQLite в памяти."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Создаём все таблицы
    Base.metadata.create_all(bind=engine)

    yield engine
    # Очистка после тестов
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_db(test_engine) -> Generator[Session, None]:
    """Создаёт сессию БД для каждого теста."""
    SessionTest = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    db = SessionTest()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(test_engine, test_db):
    """Создаёт тестовый HTTP клиент."""

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# Фикстуры для тестовых данных
@pytest.fixture
def test_person_data():
    """Тестовые данные для пользователя."""
    return {
        "first_name": "Иван",
        "last_name": "Иванов",
        "middle_name": "Иванович",
        "phone": "+79001234567",
        "passport": "1234567890",
        "email": "ivan@example.com",
        "password": "Test1234!",
    }


@pytest.fixture
def test_airport_data():
    """Тестовые данные для аэропорта."""
    return {
        "code": "SVO",
        "name": "Шереметьево",
        "city": "Москва",
    }


@pytest.fixture
def test_airline_data():
    """Тестовые данные для авиакомпании."""
    return {
        "name": "Аэрофлот",
        "code": "SU",
        "country": "Россия",
    }


@pytest.fixture
def test_flight_status_data():
    """Тестовые данные для статуса рейса."""
    return {
        "status_name": "Планируется",
    }


@pytest.fixture
def test_seat_class_data():
    """Тестовые данные для класса мест."""
    return {
        "class_name": "Эконом",
        "price_multiplier": 1.0,
        "description": "Эконом класс",
    }


@pytest.fixture
def test_model_aircraft_data():
    """Тестовые данные для модели самолёта."""
    return {
        "name": "Boeing 737",
        "manufacturer": "Boeing",
        "seats": [
            {"class_id": 1, "count": 150},
        ],
    }


@pytest.fixture
def test_aircraft_data():
    """Тестовые данные для самолёта."""
    return {
        "registration_number": "RA-12345",
        "id_model": 1,
        "manufacture_year": 2020,
        "last_maintenance": "2024-01-01",
    }
