"""Тесты для CRUD операций."""

import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.models.base import Base
from backend.app.crud import person as person_crud
from backend.app.crud import flight as flight_crud
from backend.app.crud import aircraft as aircraft_crud
from backend.app.crud import ticket as ticket_crud
from backend.app.schemas.person import PersonCreate
from backend.app.schemas.flight import AirportCreate, AirlineCreate, FlightStatusCreate
from backend.app.schemas.aircraft import SeatClassCreate
from backend.app.schemas.ticket import TicketStatusCreate
from backend.app.auth.hashing import hash_password


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


# =========================================================
# PERSON CRUD TESTS
# =========================================================


class TestPersonCRUD:
    """Тесты для CRUD операций с пользователями."""

    def test_create_person(self, test_db):
        """Создание пользователя."""
        payload = PersonCreate(
            first_name="Иван",
            last_name="Иванов",
            middle_name="Иванович",
            phone="+79001234567",
            passport="1234567890",
            email="ivan@example.com",
            password="Test1234!",
        )

        person = person_crud.create_person(test_db, payload)

        assert person.email == "ivan@example.com"
        assert person.password_hash is not None

    def test_get_person(self, test_db):
        """Получение пользователя по ID."""
        payload = PersonCreate(
            first_name="Иван",
            last_name="Иванов",
            middle_name="Иванович",
            phone="+79001234567",
            passport="1234567890",
            email="ivan@example.com",
            password="Test1234!",
        )
        created = person_crud.create_person(test_db, payload)

        retrieved = person_crud.get_person(test_db, created.id)

        assert retrieved.id == created.id

    def test_get_by_email(self, test_db):
        """Получение пользователя по email."""
        payload = PersonCreate(
            first_name="Иван",
            last_name="Иванов",
            middle_name="Иванович",
            phone="+79001234567",
            passport="1234567890",
            email="ivan@example.com",
            password="Test1234!",
        )
        created = person_crud.create_person(test_db, payload)

        retrieved = person_crud.get_by_email(test_db, "ivan@example.com")

        assert retrieved.id == created.id

    def test_get_by_passport(self, test_db):
        """Получение пользователя по паспорту."""
        payload = PersonCreate(
            first_name="Иван",
            last_name="Иванов",
            middle_name="Иванович",
            phone="+79001234567",
            passport="1234567890",
            email="ivan@example.com",
            password="Test1234!",
        )
        created = person_crud.create_person(test_db, payload)

        retrieved = person_crud.get_by_passport(test_db, "1234567890")

        assert retrieved.id == created.id

    def test_update_person(self, test_db):
        """Обновление пользователя."""
        payload = PersonCreate(
            first_name="Иван",
            last_name="Иванов",
            middle_name="Иванович",
            phone="+79001234567",
            passport="1234567890",
            email="ivan@example.com",
            password="Test1234!",
        )
        created = person_crud.create_person(test_db, payload)

        from backend.app.schemas.person import PersonUpdate

        update_payload = PersonUpdate(first_name="Петр")

        updated = person_crud.update_person(test_db, created, update_payload)

        assert updated.first_name == "Петр"

    def test_delete_person(self, test_db):
        """Удаление пользователя."""
        payload = PersonCreate(
            first_name="Иван",
            last_name="Иванов",
            middle_name="Иванович",
            phone="+79001234567",
            passport="1234567890",
            email="ivan@example.com",
            password="Test1234!",
        )
        created = person_crud.create_person(test_db, payload)

        result = person_crud.delete_person(test_db, created)

        assert result["deleted_id"] == created.id
        assert person_crud.get_person(test_db, created.id) is None

    def test_change_password(self, test_db):
        """Смена пароля."""
        payload = PersonCreate(
            first_name="Иван",
            last_name="Иванов",
            middle_name="Иванович",
            phone="+79001234567",
            passport="1234567890",
            email="ivan@example.com",
            password="Test1234!",
        )
        created = person_crud.create_person(test_db, payload)

        updated = person_crud.change_password(test_db, created, "NewPass123!")

        # Пароли должны быть разными
        assert updated.password_hash is not None
        assert len(updated.password_hash) > 0

    def test_get_all(self, test_db):
        """Получение всех пользователей."""
        for i in range(3):
            payload = PersonCreate(
                first_name=f"Иван{i}",
                last_name="Иванов",
                middle_name="Иванович",
                phone="+79001234567",
                passport=f"123456789{i}",
                email=f"ivan{i}@example.com",
                password="Test1234!",
            )
            person_crud.create_person(test_db, payload)

        all_persons = person_crud.get_all(test_db)

        assert len(all_persons) == 3


# =========================================================
# FLIGHT CRUD TESTS
# =========================================================


class TestFlightCRUD:
    """Тесты для CRUD операций с рейсами."""

    def test_create_airport(self, test_db):
        """Создание аэропорта."""
        payload = AirportCreate(code="SVO", name="Шереметьево", city="Москва")

        airport = flight_crud.create_airport(test_db, payload)

        assert airport.code == "SVO"

    def test_get_airport_by_code(self, test_db):
        """Получение аэропорта по коду."""
        payload = AirportCreate(code="SVO", name="Шереметьево", city="Москва")
        created = flight_crud.create_airport(test_db, payload)

        retrieved = flight_crud.get_airport_by_code(test_db, "SVO")

        assert retrieved.id == created.id

    def test_count_departing_flights(self, test_db):
        """Подсчёт вылетающих рейсов."""
        # Создаём аэропорты
        airport1 = flight_crud.create_airport(
            test_db, AirportCreate(code="SVO", name="Шереметьево", city="Москва")
        )
        airport2 = flight_crud.create_airport(
            test_db, AirportCreate(code="LED", name="Пулково", city="СПб")
        )

        assert flight_crud.count_departing_flights(test_db, airport1.id) == 0

    def test_count_arriving_flights(self, test_db):
        """Подсчёт прибывающих рейсов."""
        airport1 = flight_crud.create_airport(
            test_db, AirportCreate(code="SVO", name="Шереметьево", city="Москва")
        )

        assert flight_crud.count_arriving_flights(test_db, airport1.id) == 0

    def test_create_airline(self, test_db):
        """Создание авиакомпании."""
        payload = AirlineCreate(name="Аэрофлот", code="SU", country="Россия")

        airline = flight_crud.create_airline(test_db, payload)

        assert airline.code == "SU"

    def test_create_flight_status(self, test_db):
        """Создание статуса рейса."""
        payload = FlightStatusCreate(status_name="Планируется")

        status = flight_crud.create_flight_status(test_db, payload)

        assert status.status_name == "Планируется"

    def test_count_status_flights(self, test_db):
        """Подсчёт рейсов со статусом."""
        status = flight_crud.create_flight_status(
            test_db, FlightStatusCreate(status_name="Планируется")
        )

        assert flight_crud.count_status_flights(test_db, status.id) == 0


# =========================================================
# AIRCRAFT CRUD TESTS
# =========================================================


class TestAircraftCRUD:
    """Тесты для CRUD операций с самолётами."""

    def test_create_seat_class(self, test_db):
        """Создание класса мест."""
        payload = SeatClassCreate(
            class_name="Эконом", price_multiplier=1.0, description="Эконом"
        )

        seat_class = aircraft_crud.create_seat_class(test_db, payload)

        assert seat_class.class_name == "Эконом"

    def test_count_seat_class_model_seats(self, test_db):
        """Подсчёт распределений мест для класса."""
        seat_class = aircraft_crud.create_seat_class(
            test_db,
            SeatClassCreate(
                class_name="Эконом", price_multiplier=1.0, description="Эконом"
            ),
        )

        assert aircraft_crud.count_seat_class_model_seats(test_db, seat_class.id) == 0


# =========================================================
# TICKET CRUD TESTS
# =========================================================


class TestTicketCRUD:
    """Тесты для CRUD операций с билетами."""

    def test_create_ticket_status(self, test_db):
        """Создание статуса билета."""
        from backend.app.schemas.ticket import TicketStatusCreate

        payload = TicketStatusCreate(status_name="Подтверждён")

        status = ticket_crud.create_ticket_status(test_db, payload)

        assert status.status_name == "Подтверждён"

    def test_count_status_tickets(self, test_db):
        """Подсчёт билетов со статусом."""
        from backend.app.schemas.ticket import TicketStatusCreate

        status = ticket_crud.create_ticket_status(
            test_db, TicketStatusCreate(status_name="Подтверждён")
        )

        assert ticket_crud.count_status_tickets(test_db, status.id) == 0

    def test_check_seat_occupied(self, test_db):
        """Проверка занятости места."""
        from backend.app.models import Flight, SeatClass, Ticket, Person, TicketStatus
        from decimal import Decimal

        flight = Flight(
            flight_number="SU100",
            departure_datetime=datetime.now(timezone.utc) + timedelta(days=1),
            arrival_datetime=datetime.now(timezone.utc) + timedelta(days=1, hours=2),
            id_from=1,
            id_to=2,
            id_airline=1,
            id_aircraft=1,
            id_status=1,
        )
        seat_class = SeatClass(
            class_name="Эконом", price_multiplier=1.0, description="Эконом"
        )
        person = Person(
            first_name="Иван",
            last_name="Иванов",
            email="ivan@example.com",
            passport="PASS123",
            password_hash="hash",
            phone="123",
        )
        status = TicketStatus(status_name="Подтверждён")

        test_db.add_all([flight, seat_class, person, status])
        test_db.commit()

        ticket = Ticket(
            seat_number="1A",
            id_seat_class=seat_class.id,
            price=Decimal("5000.00"),
            id_status=status.id,
            id_flight=flight.id,
            id_passenger=person.id,
        )
        test_db.add(ticket)
        test_db.commit()

        assert ticket_crud.check_seat_occupied(test_db, flight.id, "1A") is True
        assert ticket_crud.check_seat_occupied(test_db, flight.id, "1B") is False
