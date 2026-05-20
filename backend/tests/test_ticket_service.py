"""Тесты для сервисного слоя Ticket."""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.models.base import Base
from backend.app.services.ticket import TicketService
from backend.app.schemas.ticket import TicketCreate, TicketUpdate, TicketStatusCreate
from backend.app.crud import ticket as ticket_crud


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
def ticket_service(test_db):
    """Создаёт сервис Ticket."""
    return TicketService(test_db)


@pytest.fixture
def setup_basic_data(ticket_service):
    """Создаёт базовые данные для тестов."""
    # Создаём статус билета
    status = ticket_service.create_ticket_status(TicketStatusCreate(
        status_name="Подтверждён"
    ))

    return {"status": status}


class TestTicketStatusService:
    """Тесты для управления статусами билетов."""

    def test_create_status_success(self, ticket_service):
        """Успешное создание статуса."""
        payload = TicketStatusCreate(status_name="Подтверждён")
        status = ticket_service.create_ticket_status(payload)

        assert status.status_name == "Подтверждён"

    def test_create_status_duplicate(self, ticket_service):
        """Создание статуса с дублирующимся именем."""
        payload = TicketStatusCreate(status_name="Подтверждён")
        ticket_service.create_ticket_status(payload)

        with pytest.raises(ValueError, match="уже существует"):
            ticket_service.create_ticket_status(payload)


class TestTicketService:
    """Тесты для управления билетами."""

    def test_create_ticket_success(self, ticket_service, setup_basic_data):
        """Успешное создание билета."""
        from backend.app.crud import ticket as ticket_crud
        from backend.app.models import Person, Flight, SeatClass, TicketStatus

        # Создаём необходимые сущности
        person = Person(
            first_name="Иван", last_name="Иванов",
            email="ivan@example.com", passport="PASS123",
            password_hash="hash", phone="123"
        )
        seat_class = SeatClass(class_name="Эконом", price_multiplier=1.0, description="Эконом")
        flight = Flight(
            flight_number="SU100",
            departure_datetime=datetime.now(timezone.utc) + timedelta(days=1),
            arrival_datetime=datetime.now(timezone.utc) + timedelta(days=1, hours=2),
            id_from=1, id_to=2, id_airline=1, id_aircraft=1, id_status=1
        )

        ticket_service.db.add_all([person, seat_class, flight])
        ticket_service.db.commit()

        # Создаём билет
        payload = TicketCreate(
            seat_number="1A",
            id_seat_class=seat_class.id,
            price=Decimal("5000.00"),
            id_status=setup_basic_data["status"].id,
            id_flight=flight.id,
            id_passenger=person.id
        )

        ticket = ticket_service.create_ticket(payload)

        assert ticket.seat_number == "1A"
        assert ticket.price == Decimal("5000.00")
        assert ticket.id_flight == flight.id

    def test_create_ticket_duplicate_seat(self, ticket_service, setup_basic_data):
        """Создание билета на занятое место."""
        from backend.app.crud import ticket as ticket_crud
        from backend.app.models import Person, Flight, SeatClass, TicketStatus

        person = Person(
            first_name="Иван", last_name="Иванов",
            email="ivan@example.com", passport="PASS123",
            password_hash="hash", phone="123"
        )
        seat_class = SeatClass(class_name="Эконом", price_multiplier=1.0, description="Эконом")
        flight = Flight(
            flight_number="SU100",
            departure_datetime=datetime.now(timezone.utc) + timedelta(days=1),
            arrival_datetime=datetime.now(timezone.utc) + timedelta(days=1, hours=2),
            id_from=1, id_to=2, id_airline=1, id_aircraft=1, id_status=1
        )

        ticket_service.db.add_all([person, seat_class, flight])
        ticket_service.db.commit()

        payload = TicketCreate(
            seat_number="1A",
            id_seat_class=seat_class.id,
            price=Decimal("5000.00"),
            id_status=setup_basic_data["status"].id,
            id_flight=flight.id,
            id_passenger=person.id
        )

        ticket_service.create_ticket(payload)

        # Пробуем создать билет на то же место
        payload2 = TicketCreate(
            seat_number="1A",
            id_seat_class=seat_class.id,
            price=Decimal("5000.00"),
            id_status=setup_basic_data["status"].id,
            id_flight=flight.id,
            id_passenger=person.id
        )

        with pytest.raises(ValueError, match="уже занято"):
            ticket_service.create_ticket(payload2)

    def test_create_ticket_nonexistent_flight(self, ticket_service):
        """Создание билета на несуществующий рейс."""
        payload = TicketCreate(
            seat_number="1A",
            id_seat_class=1,
            price=Decimal("5000.00"),
            id_status=1,
            id_flight=9999,
            id_passenger=1
        )

        with pytest.raises(ValueError, match="Рейс не найден"):
            ticket_service.create_ticket(payload)

    def test_update_ticket(self, ticket_service, setup_basic_data):
        """Обновление билета."""
        from backend.app.models import Person, Flight, SeatClass

        person = Person(
            first_name="Иван", last_name="Иванов",
            email="ivan@example.com", passport="PASS123",
            password_hash="hash", phone="123"
        )
        seat_class = SeatClass(class_name="Эконом", price_multiplier=1.0, description="Эконом")
        flight = Flight(
            flight_number="SU100",
            departure_datetime=datetime.now(timezone.utc) + timedelta(days=1),
            arrival_datetime=datetime.now(timezone.utc) + timedelta(days=1, hours=2),
            id_from=1, id_to=2, id_airline=1, id_aircraft=1, id_status=1
        )

        ticket_service.db.add_all([person, seat_class, flight])
        ticket_service.db.commit()

        ticket = ticket_service.create_ticket(TicketCreate(
            seat_number="1A",
            id_seat_class=seat_class.id,
            price=Decimal("5000.00"),
            id_status=setup_basic_data["status"].id,
            id_flight=flight.id,
            id_passenger=person.id
        ))

        updated = ticket_service.update_ticket(ticket.id, TicketUpdate(price=Decimal("6000.00")))

        assert updated.price == Decimal("6000.00")

    def test_cancel_ticket(self, ticket_service, setup_basic_data):
        """Отмена билета."""
        from backend.app.models import Person, Flight, SeatClass

        person = Person(
            first_name="Иван", last_name="Иванов",
            email="ivan@example.com", passport="PASS123",
            password_hash="hash", phone="123"
        )
        seat_class = SeatClass(class_name="Эконом", price_multiplier=1.0, description="Эконом")
        flight = Flight(
            flight_number="SU100",
            departure_datetime=datetime.now(timezone.utc) + timedelta(days=1),
            arrival_datetime=datetime.now(timezone.utc) + timedelta(days=1, hours=2),
            id_from=1, id_to=2, id_airline=1, id_aircraft=1, id_status=1
        )

        ticket_service.db.add_all([person, seat_class, flight])
        ticket_service.db.commit()

        # Создаём статус "Отменён"
        cancelled_status = TicketStatusCreate(status_name="Отменён")
        ticket_service.create_ticket_status(cancelled_status)

        ticket = ticket_service.create_ticket(TicketCreate(
            seat_number="1A",
            id_seat_class=seat_class.id,
            price=Decimal("5000.00"),
            id_status=setup_basic_data["status"].id,
            id_flight=flight.id,
            id_passenger=person.id
        ))

        cancelled = ticket_service.cancel_ticket(ticket.id)

        assert cancelled.id_status != setup_basic_data["status"].id

    def test_delete_ticket(self, ticket_service, setup_basic_data):
        """Удаление билета."""
        from backend.app.models import Person, Flight, SeatClass

        person = Person(
            first_name="Иван", last_name="Иванов",
            email="ivan@example.com", passport="PASS123",
            password_hash="hash", phone="123"
        )
        seat_class = SeatClass(class_name="Эконом", price_multiplier=1.0, description="Эконом")
        flight = Flight(
            flight_number="SU100",
            departure_datetime=datetime.now(timezone.utc) + timedelta(days=1),
            arrival_datetime=datetime.now(timezone.utc) + timedelta(days=1, hours=2),
            id_from=1, id_to=2, id_airline=1, id_aircraft=1, id_status=1
        )

        ticket_service.db.add_all([person, seat_class, flight])
        ticket_service.db.commit()

        ticket = ticket_service.create_ticket(TicketCreate(
            seat_number="1A",
            id_seat_class=seat_class.id,
            price=Decimal("5000.00"),
            id_status=setup_basic_data["status"].id,
            id_flight=flight.id,
            id_passenger=person.id
        ))

        result = ticket_service.delete_ticket(ticket.id)

        assert result["message"] == "Билет успешно удален"
        assert ticket_service.get_ticket(ticket.id) is None

    def test_get_all_tickets(self, ticket_service, setup_basic_data):
        """Получение всех билетов."""
        from backend.app.models import Person, Flight, SeatClass

        person = Person(
            first_name="Иван", last_name="Иванов",
            email="ivan@example.com", passport="PASS123",
            password_hash="hash", phone="123"
        )
        seat_class = SeatClass(class_name="Эконом", price_multiplier=1.0, description="Эконом")
        flight = Flight(
            flight_number="SU100",
            departure_datetime=datetime.now(timezone.utc) + timedelta(days=1),
            arrival_datetime=datetime.now(timezone.utc) + timedelta(days=1, hours=2),
            id_from=1, id_to=2, id_airline=1, id_aircraft=1, id_status=1
        )

        ticket_service.db.add_all([person, seat_class, flight])
        ticket_service.db.commit()

        ticket_service.create_ticket(TicketCreate(
            seat_number="1A",
            id_seat_class=seat_class.id,
            price=Decimal("5000.00"),
            id_status=setup_basic_data["status"].id,
            id_flight=flight.id,
            id_passenger=person.id
        ))

        tickets = ticket_service.get_all_tickets()

        assert len(tickets) >= 1

    def test_search_tickets(self, ticket_service, setup_basic_data):
        """Поиск билетов."""
        from backend.app.models import Person, Flight, SeatClass
        from backend.app.schemas.ticket import TicketSearch

        person = Person(
            first_name="Иван", last_name="Иванов",
            email="ivan@example.com", passport="PASS123",
            password_hash="hash", phone="123"
        )
        seat_class = SeatClass(class_name="Эконом", price_multiplier=1.0, description="Эконом")
        flight = Flight(
            flight_number="SU100",
            departure_datetime=datetime.now(timezone.utc) + timedelta(days=1),
            arrival_datetime=datetime.now(timezone.utc) + timedelta(days=1, hours=2),
            id_from=1, id_to=2, id_airline=1, id_aircraft=1, id_status=1
        )

        ticket_service.db.add_all([person, seat_class, flight])
        ticket_service.db.commit()

        ticket_service.create_ticket(TicketCreate(
            seat_number="1A",
            id_seat_class=seat_class.id,
            price=Decimal("5000.00"),
            id_status=setup_basic_data["status"].id,
            id_flight=flight.id,
            id_passenger=person.id
        ))

        criteria = TicketSearch(id_passenger=person.id)
        results = ticket_service.search_tickets(criteria)

        assert len(results) >= 1

    def test_get_tickets_by_passenger(self, ticket_service, setup_basic_data):
        """Получение билетов пассажира."""
        from backend.app.models import Person, Flight, SeatClass

        person = Person(
            first_name="Иван", last_name="Иванов",
            email="ivan@example.com", passport="PASS123",
            password_hash="hash", phone="123"
        )
        seat_class = SeatClass(class_name="Эконом", price_multiplier=1.0, description="Эконом")
        flight = Flight(
            flight_number="SU100",
            departure_datetime=datetime.now(timezone.utc) + timedelta(days=1),
            arrival_datetime=datetime.now(timezone.utc) + timedelta(days=1, hours=2),
            id_from=1, id_to=2, id_airline=1, id_aircraft=1, id_status=1
        )

        ticket_service.db.add_all([person, seat_class, flight])
        ticket_service.db.commit()

        ticket_service.create_ticket(TicketCreate(
            seat_number="1A",
            id_seat_class=seat_class.id,
            price=Decimal("5000.00"),
            id_status=setup_basic_data["status"].id,
            id_flight=flight.id,
            id_passenger=person.id
        ))

        tickets = ticket_service.get_tickets_by_passenger(person.id)

        assert len(tickets) >= 1

    def test_get_tickets_by_flight(self, ticket_service, setup_basic_data):
        """Получение билетов на рейс."""
        from backend.app.models import Person, Flight, SeatClass

        person = Person(
            first_name="Иван", last_name="Иванов",
            email="ivan@example.com", passport="PASS123",
            password_hash="hash", phone="123"
        )
        seat_class = SeatClass(class_name="Эконом", price_multiplier=1.0, description="Эконом")
        flight = Flight(
            flight_number="SU100",
            departure_datetime=datetime.now(timezone.utc) + timedelta(days=1),
            arrival_datetime=datetime.now(timezone.utc) + timedelta(days=1, hours=2),
            id_from=1, id_to=2, id_airline=1, id_aircraft=1, id_status=1
        )

        ticket_service.db.add_all([person, seat_class, flight])
        ticket_service.db.commit()

        ticket_service.create_ticket(TicketCreate(
            seat_number="1A",
            id_seat_class=seat_class.id,
            price=Decimal("5000.00"),
            id_status=setup_basic_data["status"].id,
            id_flight=flight.id,
            id_passenger=person.id
        ))

        tickets = ticket_service.get_tickets_by_flight(flight.id)

        assert len(tickets) >= 1
