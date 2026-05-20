"""Тесты для сервисного слоя Flight."""

import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.models.base import Base
from backend.app.services.flight import FlightService
from backend.app.schemas.flight import (
    AirportCreate,
    AirlineCreate,
    FlightStatusCreate,
    FlightCreate,
    FlightUpdate,
)


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
def flight_service(test_db):
    """Создаёт сервис Flight."""
    return FlightService(test_db)


@pytest.fixture
def setup_basic_data(flight_service, test_db):
    """Создаёт базовые данные для тестов."""
    # Создаём аэропорты
    airport1 = flight_service.create_airport(
        AirportCreate(code="SVO", name="Шереметьево", city="Москва")
    )
    airport2 = flight_service.create_airport(
        AirportCreate(code="LED", name="Пулково", city="Санкт-Петербург")
    )

    # Создаём авиакомпанию
    airline = flight_service.create_airline(
        AirlineCreate(name="Аэрофлот", code="SU", country="Россия")
    )

    # Создаём статус
    status = flight_service.create_flight_status(
        FlightStatusCreate(status_name="Планируется")
    )

    # Создаём модель самолёта через CRUD
    from backend.app.crud import aircraft as aircraft_crud
    from backend.app.schemas.aircraft import SeatClassCreate, ModelAircraftCreate

    seat_class = aircraft_crud.create_seat_class(
        test_db,
        SeatClassCreate(
            class_name="Эконом", price_multiplier=1.0, description="Эконом"
        ),
    )

    model = aircraft_crud.create_model_aircraft(
        test_db,
        ModelAircraftCreate(
            name="Boeing 737",
            manufacturer="Boeing",
            seats=[{"class_id": seat_class.id, "count": 150}],
        ),
    )

    # Создаём самолёт
    from backend.app.schemas.aircraft import AircraftCreate

    aircraft = aircraft_crud.create_aircraft(
        test_db,
        AircraftCreate(
            registration_number="RA-12345",
            id_model=model.id,
            manufacture_year=2020,
            last_maintenance="2024-01-01",
        ),
    )

    return {
        "airport1": airport1,
        "airport2": airport2,
        "airline": airline,
        "status": status,
        "aircraft": aircraft,
    }


class TestAirportService:
    """Тесты для управления аэропортами."""

    def test_create_airport_success(self, flight_service):
        """Успешное создание аэропорта."""
        payload = AirportCreate(code="SVO", name="Шереметьево", city="Москва")
        airport = flight_service.create_airport(payload)

        assert airport.code == "SVO"
        assert airport.name == "Шереметьево"
        assert airport.city == "Москва"

    def test_create_airport_duplicate_code(self, flight_service):
        """Создание аэропорта с дублирующимся кодом."""
        payload = AirportCreate(code="SVO", name="Шереметьево", city="Москва")
        flight_service.create_airport(payload)

        with pytest.raises(ValueError, match="уже существует"):
            flight_service.create_airport(payload)

    def test_delete_airport_with_flights(self, flight_service, setup_basic_data):
        """Удаление аэропорта с зависимыми рейсами."""
        from backend.app.schemas.flight import FlightCreate

        airport1 = setup_basic_data["airport1"]
        airport2 = setup_basic_data["airport2"]
        airline = setup_basic_data["airline"]
        status = setup_basic_data["status"]
        aircraft = setup_basic_data["aircraft"]

        # Создаём рейс
        flight_data = FlightCreate(
            flight_number="SU100",
            departure_datetime=datetime.now(timezone.utc) + timedelta(days=1),
            arrival_datetime=datetime.now(timezone.utc) + timedelta(days=1, hours=2),
            id_from=airport1.id,
            id_to=airport2.id,
            id_airline=airline.id,
            id_aircraft=aircraft.id,
            id_status=status.id,
        )
        flight_service.create_flight(flight_data)

        # Пробуем удалить аэропорт
        with pytest.raises(ValueError, match="есть.*рейсов"):
            flight_service.delete_airport(airport1.id)

    def test_delete_airport_success(self, flight_service):
        """Успешное удаление аэропорта без зависимостей."""
        airport = flight_service.create_airport(
            AirportCreate(code="VKO", name="Внуково", city="Москва")
        )

        result = flight_service.delete_airport(airport.id)

        assert result["message"] == "Аэропорт успешно удален"
        assert flight_service.get_airport(airport.id) is None


class TestAirlineService:
    """Тесты для управления авиакомпаниями."""

    def test_create_airline_success(self, flight_service):
        """Успешное создание авиакомпании."""
        payload = AirlineCreate(name="Аэрофлот", code="SU", country="Россия")
        airline = flight_service.create_airline(payload)

        assert airline.code == "SU"
        assert airline.name == "Аэрофлот"

    def test_create_airline_duplicate_code(self, flight_service):
        """Создание авиакомпании с дублирующимся кодом."""
        payload = AirlineCreate(name="Аэрофлот", code="SU", country="Россия")
        flight_service.create_airline(payload)

        with pytest.raises(ValueError, match="уже существует"):
            flight_service.create_airline(payload)


class TestFlightStatusService:
    """Тесты для управления статусами рейсов."""

    def test_create_status_success(self, flight_service):
        """Успешное создание статуса."""
        payload = FlightStatusCreate(status_name="Планируется")
        status = flight_service.create_flight_status(payload)

        assert status.status_name == "Планируется"

    def test_create_status_duplicate(self, flight_service):
        """Создание статуса с дублирующимся именем."""
        payload = FlightStatusCreate(status_name="Планируется")
        flight_service.create_flight_status(payload)

        with pytest.raises(ValueError, match="уже существует"):
            flight_service.create_flight_status(payload)


class TestFlightService:
    """Тесты для управления рейсами."""

    def test_create_flight_success(self, flight_service, setup_basic_data):
        """Успешное создание рейса."""
        from backend.app.schemas.flight import FlightCreate

        flight_data = FlightCreate(
            flight_number="SU100",
            departure_datetime=datetime.now(timezone.utc) + timedelta(days=1),
            arrival_datetime=datetime.now(timezone.utc) + timedelta(days=1, hours=2),
            id_from=setup_basic_data["airport1"].id,
            id_to=setup_basic_data["airport2"].id,
            id_airline=setup_basic_data["airline"].id,
            id_aircraft=setup_basic_data["aircraft"].id,
            id_status=setup_basic_data["status"].id,
        )

        flight = flight_service.create_flight(flight_data)

        assert flight.flight_number == "SU100"
        assert flight.id_from == setup_basic_data["airport1"].id

    def test_create_flight_past_datetime(self, flight_service, setup_basic_data):
        """Создание рейса в прошлом."""
        from backend.app.schemas.flight import FlightCreate

        flight_data = FlightCreate(
            flight_number="SU100",
            departure_datetime=datetime.now(timezone.utc) - timedelta(days=1),
            arrival_datetime=datetime.now(timezone.utc),
            id_from=setup_basic_data["airport1"].id,
            id_to=setup_basic_data["airport2"].id,
            id_airline=setup_basic_data["airline"].id,
            id_aircraft=setup_basic_data["aircraft"].id,
            id_status=setup_basic_data["status"].id,
        )

        with pytest.raises(ValueError, match="в прошлом"):
            flight_service.create_flight(flight_data)

    def test_create_flight_same_airport(self, flight_service, setup_basic_data):
        """Создание рейса с одинаковыми аэропортами."""
        from backend.app.schemas.flight import FlightCreate

        flight_data = FlightCreate(
            flight_number="SU100",
            departure_datetime=datetime.now(timezone.utc) + timedelta(days=1),
            arrival_datetime=datetime.now(timezone.utc) + timedelta(days=1, hours=2),
            id_from=setup_basic_data["airport1"].id,
            id_to=setup_basic_data["airport1"].id,
            id_airline=setup_basic_data["airline"].id,
            id_aircraft=setup_basic_data["aircraft"].id,
            id_status=setup_basic_data["status"].id,
        )

        with pytest.raises(ValueError, match="не могут совпадать"):
            flight_service.create_flight(flight_data)

    def test_create_flight_arrival_before_departure(
        self, flight_service, setup_basic_data
    ):
        """Создание рейса с временем прилёта до вылета."""
        from backend.app.schemas.flight import FlightCreate

        flight_data = FlightCreate(
            flight_number="SU100",
            departure_datetime=datetime.now(timezone.utc) + timedelta(days=1, hours=2),
            arrival_datetime=datetime.now(timezone.utc) + timedelta(days=1),
            id_from=setup_basic_data["airport1"].id,
            id_to=setup_basic_data["airport2"].id,
            id_airline=setup_basic_data["airline"].id,
            id_aircraft=setup_basic_data["aircraft"].id,
            id_status=setup_basic_data["status"].id,
        )

        with pytest.raises(ValueError, match="после времени вылета"):
            flight_service.create_flight(flight_data)

    def test_delete_flight_with_tickets(self, flight_service, setup_basic_data):
        """Удаление рейса с проданными билетами."""
        from backend.app.schemas.flight import FlightCreate
        from backend.app.crud import flight as flight_crud

        flight_data = FlightCreate(
            flight_number="SU100",
            departure_datetime=datetime.now(timezone.utc) + timedelta(days=1),
            arrival_datetime=datetime.now(timezone.utc) + timedelta(days=1, hours=2),
            id_from=setup_basic_data["airport1"].id,
            id_to=setup_basic_data["airport2"].id,
            id_airline=setup_basic_data["airline"].id,
            id_aircraft=setup_basic_data["aircraft"].id,
            id_status=setup_basic_data["status"].id,
        )
        flight = flight_service.create_flight(flight_data)

        # Создаём билет напрямую через CRUD
        from backend.app.models import Ticket, Person
        from backend.app.auth.hashing import hash_password

        person = Person(
            first_name="Test",
            last_name="Test",
            email="test@test.com",
            passport="PASS1234567890",
            password_hash=hash_password("pass"),
            phone="123",
        )
        flight_service.db.add(person)
        flight_service.db.commit()

        ticket = Ticket(
            seat_number="1A",
            id_seat_class=1,
            price=5000.0,
            id_status=1,
            id_flight=flight.id,
            id_passenger=person.id,
        )
        flight_service.db.add(ticket)
        flight_service.db.commit()

        # Пробуем удалить рейс
        with pytest.raises(ValueError, match="проданных билетов"):
            flight_service.delete_flight(flight.id)

    def test_search_flights(self, flight_service, setup_basic_data):
        """Поиск рейсов."""
        from backend.app.schemas.flight import FlightCreate, FlightSearch
        from backend.app.schemas.flight import AirportCreate, AirlineCreate, FlightStatusCreate

        # Создаём ещё один рейс
        flight_data = FlightCreate(
            flight_number="SU200",
            departure_datetime=datetime.now(timezone.utc) + timedelta(days=2),
            arrival_datetime=datetime.now(timezone.utc) + timedelta(days=2, hours=2),
            id_from=setup_basic_data["airport1"].id,
            id_to=setup_basic_data["airport2"].id,
            id_airline=setup_basic_data["airline"].id,
            id_aircraft=setup_basic_data["aircraft"].id,
            id_status=setup_basic_data["status"].id,
        )
        flight_service.create_flight(flight_data)

        # Ищем по аэропорту вылета
        criteria = FlightSearch(id_from=setup_basic_data["airport1"].id)
        results = flight_service.search_flights(criteria)

        assert len(results) >= 1

    def test_get_all_flights(self, flight_service, setup_basic_data):
        """Получение всех рейсов."""
        from backend.app.schemas.flight import FlightCreate

        flight_data = FlightCreate(
            flight_number="SU100",
            departure_datetime=datetime.now(timezone.utc) + timedelta(days=1),
            arrival_datetime=datetime.now(timezone.utc) + timedelta(days=1, hours=2),
            id_from=setup_basic_data["airport1"].id,
            id_to=setup_basic_data["airport2"].id,
            id_airline=setup_basic_data["airline"].id,
            id_aircraft=setup_basic_data["aircraft"].id,
            id_status=setup_basic_data["status"].id,
        )
        flight_service.create_flight(flight_data)

        results = flight_service.get_all_flights()

        assert len(results) >= 1
