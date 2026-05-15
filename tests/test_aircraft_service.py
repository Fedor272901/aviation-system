"""Тесты для сервисного слоя Aircraft."""

import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.base import Base
from app.services.aircraft import AircraftService
from app.schemas.aircraft import (
    SeatClassCreate,
    ModelAircraftCreate,
    AircraftCreate,
    AircraftLeaseCreate,
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
def aircraft_service(test_db):
    """Создаёт сервис Aircraft."""
    return AircraftService(test_db)


@pytest.fixture
def setup_basic_data(aircraft_service):
    """Создаёт базовые данные для тестов."""
    # Создаём класс мест
    seat_class = aircraft_service.create_seat_class(
        SeatClassCreate(
            class_name="Эконом", price_multiplier=1.0, description="Эконом класс"
        )
    )

    # Создаём модель самолёта
    model = aircraft_service.create_model_aircraft(
        ModelAircraftCreate(
            name="Boeing 737",
            manufacturer="Boeing",
            seats=[{"class_id": seat_class.id, "count": 150}],
        )
    )

    return {
        "seat_class": seat_class,
        "model": model,
    }


class TestSeatClassService:
    """Тесты для управления классами мест."""

    def test_create_seat_class_success(self, aircraft_service):
        """Успешное создание класса мест."""
        payload = SeatClassCreate(
            class_name="Бизнес", price_multiplier=1.5, description="Бизнес класс"
        )
        seat_class = aircraft_service.create_seat_class(payload)

        assert seat_class.class_name == "Бизнес"
        assert seat_class.price_multiplier == 1.5

    def test_create_seat_class_duplicate(self, aircraft_service):
        """Создание класса мест с дублирующимся именем."""
        payload = SeatClassCreate(
            class_name="Эконом", price_multiplier=1.0, description="Эконом"
        )
        aircraft_service.create_seat_class(payload)

        with pytest.raises(ValueError, match="уже существует"):
            aircraft_service.create_seat_class(payload)

    def test_update_seat_class(self, aircraft_service):
        """Обновление класса мест."""
        payload = SeatClassCreate(
            class_name="Эконом", price_multiplier=1.0, description="Эконом"
        )
        seat_class = aircraft_service.create_seat_class(payload)

        updated = aircraft_service.update_seat_class(
            seat_class.id,
            SeatClassCreate(
                class_name="Эконом", price_multiplier=1.2, description="Обновлённый"
            ),
        )

        assert float(updated.price_multiplier) == 1.2
        assert updated.description == "Обновлённый"

    def test_delete_seat_class_success(self, aircraft_service):
        """Успешное удаление класса мест."""
        from app.schemas.aircraft import SeatClassCreate

        payload = SeatClassCreate(
            class_name="Эконом", price_multiplier=1.5, description="Тест"
        )
        seat_class = aircraft_service.create_seat_class(payload)

        result = aircraft_service.delete_seat_class(seat_class.id)

        assert result["message"] == "Класс мест успешно удален"
        assert aircraft_service.get_seat_class(seat_class.id) is None


class TestModelAircraftService:
    """Тесты для управления моделями самолётов."""

    def test_create_model_success(self, aircraft_service):
        """Успешное создание модели самолёта."""
        # Сначала создаём класс мест
        seat_class = aircraft_service.create_seat_class(
            SeatClassCreate(
                class_name="Эконом", price_multiplier=1.0, description="Эконом"
            )
        )

        payload = ModelAircraftCreate(
            name="Airbus A320",
            manufacturer="Airbus",
            seats=[{"class_id": seat_class.id, "count": 180}],
        )
        model = aircraft_service.create_model_aircraft(payload)

        assert model.name == "Airbus A320"
        assert model.manufacturer == "Airbus"

    def test_delete_model_with_aircraft(self, aircraft_service, setup_basic_data):
        """Удаление модели с зависимыми самолётами."""
        from app.schemas.aircraft import AircraftCreate

        model = setup_basic_data["model"]

        # Создаём самолёт этой модели
        aircraft_data = AircraftCreate(
            registration_number="RA-12345",
            id_model=model.id,
            manufacture_year=2020,
            last_maintenance="2024-01-01",
        )
        aircraft_service.create_aircraft(aircraft_data)

        # Пробуем удалить модель
        with pytest.raises(ValueError, match="самолётов используют её"):
            aircraft_service.delete_model_aircraft(model.id)

    def test_delete_model_success(self, aircraft_service):
        """Успешное удаление модели без зависимостей."""
        # Создаём класс мест без распределений
        seat_class = aircraft_service.create_seat_class(
            SeatClassCreate(class_name="Тест", price_multiplier=1.0, description="Тест")
        )

        # Создаём модель без распределений (пустой список seats)
        model = aircraft_service.create_model_aircraft(
            ModelAircraftCreate(
                name="Test Model",
                manufacturer="Test",
                seats=[],  # Нет распределений
            )
        )

        result = aircraft_service.delete_model_aircraft(model.id)

        assert result["message"] == "Модель самолёта успешно удалена"
        assert aircraft_service.get_model_aircraft(model.id) is None

    def test_update_model(self, aircraft_service, setup_basic_data):
        """Обновление модели самолёта."""
        model = setup_basic_data["model"]

        updated = aircraft_service.update_model_aircraft(
            model.id,
            ModelAircraftCreate(
                name="Boeing 737 MAX",
                manufacturer="Boeing",
                seats=[{"class_id": setup_basic_data["seat_class"].id, "count": 150}],
            ),
        )

        assert updated.name == "Boeing 737 MAX"


class TestAircraftService:
    """Тесты для управления самолётами."""

    def test_create_aircraft_success(self, aircraft_service, setup_basic_data):
        """Успешное создание самолёта."""
        payload = AircraftCreate(
            registration_number="RA-12345",
            id_model=setup_basic_data["model"].id,
            manufacture_year=2020,
            last_maintenance="2024-01-01",
        )
        aircraft = aircraft_service.create_aircraft(payload)

        assert aircraft.registration_number == "RA-12345"
        assert aircraft.id_model == setup_basic_data["model"].id

    def test_create_aircraft_duplicate_registration(
        self, aircraft_service, setup_basic_data
    ):
        """Создание самолёта с дублирующимся номером."""
        payload = AircraftCreate(
            registration_number="RA-12345",
            id_model=setup_basic_data["model"].id,
            manufacture_year=2020,
            last_maintenance="2024-01-01",
        )
        aircraft_service.create_aircraft(payload)

        with pytest.raises(ValueError, match="уже существует"):
            aircraft_service.create_aircraft(payload)

    def test_delete_aircraft_with_flights(self, aircraft_service, setup_basic_data):
        """Удаление самолёта с зависимыми рейсами."""
        from app.schemas.aircraft import AircraftCreate
        from app.crud import aircraft as aircraft_crud

        aircraft = aircraft_service.create_aircraft(
            AircraftCreate(
                registration_number="RA-12345",
                id_model=setup_basic_data["model"].id,
                manufacture_year=2020,
                last_maintenance="2024-01-01",
            )
        )

        # Создаём рейс с этим самолётом
        from app.models import Flight, Airport, Airline, FlightStatus

        airport1 = Airport(code="SVO", name="Шереметьево", city="Москва")
        airport2 = Airport(code="LED", name="Пулково", city="СПб")
        airline = Airline(name="Аэрофлот", code="SU", country="Россия")
        status = FlightStatus(status_name="Планируется")

        aircraft_service.db.add_all([airport1, airport2, airline, status])
        aircraft_service.db.commit()

        from datetime import datetime, timedelta, timezone

        flight = Flight(
            flight_number="SU100",
            departure_datetime=datetime.now(timezone.utc) + timedelta(days=1),
            arrival_datetime=datetime.now(timezone.utc) + timedelta(days=1, hours=2),
            id_from=airport1.id,
            id_to=airport2.id,
            id_airline=airline.id,
            id_aircraft=aircraft.id,
            id_status=status.id,
        )
        aircraft_service.db.add(flight)
        aircraft_service.db.commit()

        # Пробуем удалить самолёт
        with pytest.raises(ValueError, match="рейсов используют его"):
            aircraft_service.delete_aircraft(aircraft.id)

    def test_delete_aircraft_success(self, aircraft_service, setup_basic_data):
        """Успешное удаление самолёта без зависимостей."""
        aircraft = aircraft_service.create_aircraft(
            AircraftCreate(
                registration_number="RA-12345",
                id_model=setup_basic_data["model"].id,
                manufacture_year=2020,
                last_maintenance="2024-01-01",
            )
        )

        result = aircraft_service.delete_aircraft(aircraft.id)

        assert result["message"] == "Самолёт успешно удален"
        assert aircraft_service.get_aircraft(aircraft.id) is None


class TestAircraftLeaseService:
    """Тесты для управления арендами самолётов."""

    def test_create_lease_success(self, aircraft_service, setup_basic_data):
        """Успешное создание аренды."""
        from app.schemas.aircraft import AircraftCreate
        from app.crud import aircraft as aircraft_crud

        aircraft = aircraft_service.create_aircraft(
            AircraftCreate(
                registration_number="RA-12345",
                id_model=setup_basic_data["model"].id,
                manufacture_year=2020,
                last_maintenance="2024-01-01",
            )
        )

        airline = aircraft_crud.get_airline(aircraft_service.db, 1)
        if not airline:
            from app.models import Airline

            airline = Airline(name="Test Airline", code="TA", country="Test")
            aircraft_service.db.add(airline)
            aircraft_service.db.commit()

        payload = AircraftLeaseCreate(
            id_aircraft=aircraft.id,
            id_airline=airline.id,
            start_date=date.today(),
            end_date=date.today().replace(year=date.today().year + 1),
        )

        lease = aircraft_service.create_aircraft_lease(payload)

        assert lease.id_aircraft == aircraft.id
        assert lease.start_date == date.today()

    def test_create_lease_duplicate_active(self, aircraft_service, setup_basic_data):
        """Создание активной аренды при существующей."""
        from app.schemas.aircraft import AircraftCreate
        from app.crud import aircraft as aircraft_crud

        aircraft = aircraft_service.create_aircraft(
            AircraftCreate(
                registration_number="RA-12345",
                id_model=setup_basic_data["model"].id,
                manufacture_year=2020,
                last_maintenance="2024-01-01",
            )
        )

        airline = aircraft_crud.get_airline(aircraft_service.db, 1)
        if not airline:
            from app.models import Airline

            airline = Airline(name="Test Airline", code="TA", country="Test")
            aircraft_service.db.add(airline)
            aircraft_service.db.commit()

        payload1 = AircraftLeaseCreate(
            id_aircraft=aircraft.id,
            id_airline=airline.id,
            start_date=date.today(),
            end_date=None,  # Активная аренда
        )

        aircraft_service.create_aircraft_lease(payload1)

        payload2 = AircraftLeaseCreate(
            id_aircraft=aircraft.id,
            id_airline=airline.id,
            start_date=date.today(),
            end_date=date.today().replace(year=date.today().year + 1),
        )

        with pytest.raises(ValueError, match="уже есть активная аренда"):
            aircraft_service.create_aircraft_lease(payload2)

    def test_update_lease_end_date(self, aircraft_service, setup_basic_data):
        """Обновление даты окончания аренды."""
        from app.schemas.aircraft import AircraftCreate
        from app.crud import aircraft as aircraft_crud

        aircraft = aircraft_service.create_aircraft(
            AircraftCreate(
                registration_number="RA-12345",
                id_model=setup_basic_data["model"].id,
                manufacture_year=2020,
                last_maintenance="2024-01-01",
            )
        )

        airline = aircraft_crud.get_airline(aircraft_service.db, 1)
        if not airline:
            from app.models import Airline

            airline = Airline(name="Test Airline", code="TA", country="Test")
            aircraft_service.db.add(airline)
            aircraft_service.db.commit()

        lease = aircraft_service.create_aircraft_lease(
            AircraftLeaseCreate(
                id_aircraft=aircraft.id,
                id_airline=airline.id,
                start_date=date.today(),
                end_date=None,
            )
        )

        new_end_date = date.today().replace(year=date.today().year + 1)
        updated = aircraft_service.update_aircraft_lease(lease.id, new_end_date)

        assert updated.end_date == new_end_date

    def test_delete_lease(self, aircraft_service, setup_basic_data):
        """Удаление аренды."""
        from app.schemas.aircraft import AircraftCreate
        from app.crud import aircraft as aircraft_crud

        aircraft = aircraft_service.create_aircraft(
            AircraftCreate(
                registration_number="RA-12345",
                id_model=setup_basic_data["model"].id,
                manufacture_year=2020,
                last_maintenance="2024-01-01",
            )
        )

        airline = aircraft_crud.get_airline(aircraft_service.db, 1)
        if not airline:
            from app.models import Airline

            airline = Airline(name="Test Airline", code="TA", country="Test")
            aircraft_service.db.add(airline)
            aircraft_service.db.commit()

        lease = aircraft_service.create_aircraft_lease(
            AircraftLeaseCreate(
                id_aircraft=aircraft.id,
                id_airline=airline.id,
                start_date=date.today(),
                end_date=date.today().replace(year=date.today().year + 1),
            )
        )

        result = aircraft_service.delete_aircraft_lease(lease.id)

        assert result["message"] == "Аренда успешно удалена"
