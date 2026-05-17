"""Сервисный слой для сущностей Flight."""

from sqlalchemy.orm import Session
from app.crud import flight as flight_crud
from app.models import Airport, Airline, FlightStatus, Flight, Ticket
from app.schemas.flight import (
    AirportCreate,
    AirlineCreate,
    FlightStatusCreate,
    FlightCreate,
    FlightUpdate,
    FlightSearch,
)
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class FlightService:
    """Сервис для работы с рейсами."""

    def __init__(self, db: Session):
        self.db = db

    # =========================================================
    # AIRPORT
    # =========================================================

    def create_airport(self, payload: AirportCreate) -> Airport:
        """Создать аэропорт с проверкой уникальности."""
        if flight_crud.get_airport_by_code(self.db, payload.code):
            raise ValueError(f"Аэропорт с кодом '{payload.code}' уже существует")
        return flight_crud.create_airport(self.db, payload)

    def get_airport(self, airport_id: int) -> Airport | None:
        """Получить аэропорт по ID."""
        return flight_crud.get_airport(self.db, airport_id)

    def get_all_airports(self) -> list[Airport]:
        """Получить все аэропорты."""
        return flight_crud.get_all_airports(self.db)

    def update_airport(self, airport_id: int, payload: AirportCreate) -> Airport:
        """Обновить аэропорт с проверкой уникальности."""
        airport = flight_crud.get_airport(self.db, airport_id)
        if not airport:
            raise ValueError("Аэропорт не найден")

        if payload.code.upper() != airport.code:
            existing = flight_crud.get_airport_by_code(self.db, payload.code)
            if existing:
                raise ValueError(f"Аэропорт с кодом '{payload.code}' уже существует")

        return flight_crud.update_airport(self.db, airport, payload)

    def delete_airport(self, airport_id: int) -> dict:
        """Удалить аэропорт с проверкой зависимостей."""
        airport = flight_crud.get_airport(self.db, airport_id)
        if not airport:
            raise ValueError("Аэропорт не найден")

        departing_count = flight_crud.count_departing_flights(self.db, airport_id)
        arriving_count = flight_crud.count_arriving_flights(self.db, airport_id)

        if departing_count > 0 or arriving_count > 0:
            raise ValueError(
                f"Нельзя удалить аэропорт: есть {departing_count} вылетающих и "
                f"{arriving_count} прибывающих рейсов"
            )

        return flight_crud.delete_airport(self.db, airport)

    # =========================================================
    # AIRLINE
    # =========================================================

    def create_airline(self, payload: AirlineCreate) -> Airline:
        """Создать авиакомпанию с проверкой уникальности."""
        if flight_crud.get_airline_by_code(self.db, payload.code):
            raise ValueError(f"Авиакомпания с кодом '{payload.code}' уже существует")
        return flight_crud.create_airline(self.db, payload)

    def get_airline(self, airline_id: int) -> Airline | None:
        """Получить авиакомпанию по ID."""
        return flight_crud.get_airline(self.db, airline_id)

    def get_all_airlines(self) -> list[Airline]:
        """Получить все авиакомпании."""
        return flight_crud.get_all_airlines(self.db)

    def update_airline(self, airline_id: int, payload: AirlineCreate) -> Airline:
        """Обновить авиакомпанию с проверкой уникальности."""
        airline = flight_crud.get_airline(self.db, airline_id)
        if not airline:
            raise ValueError("Авиакомпания не найдена")

        if payload.code.upper() != airline.code:
            existing = flight_crud.get_airline_by_code(self.db, payload.code)
            if existing:
                raise ValueError(
                    f"Авиакомпания с кодом '{payload.code}' уже существует"
                )

        return flight_crud.update_airline(self.db, airline, payload)

    def delete_airline(self, airline_id: int) -> dict:
        """Удалить авиакомпанию с проверкой зависимостей."""
        airline = flight_crud.get_airline(self.db, airline_id)
        if not airline:
            raise ValueError("Авиакомпания не найдена")

        flights_count = flight_crud.count_airline_flights(self.db, airline_id)

        if flights_count > 0:
            raise ValueError(
                f"Нельзя удалить авиакомпанию: есть {flights_count} рейсов"
            )

        return flight_crud.delete_airline(self.db, airline)

    # =========================================================
    # FLIGHT STATUS
    # =========================================================

    def create_flight_status(self, payload: FlightStatusCreate) -> FlightStatus:
        """Создать статус рейса с проверкой уникальности."""
        if flight_crud.get_flight_status_by_name(self.db, payload.status_name):
            raise ValueError(f"Статус '{payload.status_name}' уже существует")
        return flight_crud.create_flight_status(self.db, payload)

    def get_flight_status(self, status_id: int) -> FlightStatus | None:
        """Получить статус по ID."""
        return flight_crud.get_flight_status(self.db, status_id)

    def get_all_flight_statuses(self) -> list[FlightStatus]:
        """Получить все статусы."""
        return flight_crud.get_all_flight_statuses(self.db)

    def delete_flight_status(self, status_id: int) -> dict:
        """Удалить статус с проверкой зависимостей."""
        status = flight_crud.get_flight_status(self.db, status_id)
        if not status:
            raise ValueError("Статус не найден")

        flights_count = flight_crud.count_status_flights(self.db, status_id)

        if flights_count > 0:
            raise ValueError(
                f"Нельзя удалить статус: {flights_count} рейсов используют его"
            )

        return flight_crud.delete_flight_status(self.db, status)

    # =========================================================
    # FLIGHT
    # =========================================================

    def create_flight(self, payload: FlightCreate) -> Flight:
        """Создать рейс с проверкой бизнес-правил."""
        from_airport = flight_crud.get_airport(self.db, payload.id_from)
        if not from_airport:
            raise ValueError("Аэропорт вылета не найден")

        to_airport = flight_crud.get_airport(self.db, payload.id_to)
        if not to_airport:
            raise ValueError("Аэропорт прилёта не найден")

        if payload.id_from == payload.id_to:
            raise ValueError("Аэропорт вылета и прилёта не могут совпадать")

        airline = flight_crud.get_airline(self.db, payload.id_airline)
        if not airline:
            raise ValueError("Авиакомпания не найдена")

        aircraft = flight_crud.get_aircraft(self.db, payload.id_aircraft)
        if not aircraft:
            raise ValueError("Самолёт не найден")

        status = flight_crud.get_flight_status(self.db, payload.id_status)
        if not status:
            raise ValueError("Статус рейса не найден")

        departure = payload.departure_datetime
        if departure.tzinfo is None:
            departure = departure.replace(tzinfo=timezone.utc)

        if payload.arrival_datetime <= payload.departure_datetime:
            raise ValueError("Время прилёта должно быть после времени вылета")

        if departure < datetime.now(timezone.utc):
            raise ValueError("Невозможно создать рейс в прошлом")

        return flight_crud.create_flight(self.db, payload)

    def get_flight(self, flight_id: int) -> Flight | None:
        """Получить рейс по ID."""
        return flight_crud.get_flight(self.db, flight_id)

    def get_all_flights(self, skip: int = 0, limit: int = 100) -> list[Flight]:
        """Получить все рейсы с пагинацией."""
        return flight_crud.get_all_flights(self.db, skip, limit)

    def update_flight(self, flight_id: int, payload: FlightUpdate) -> Flight:
        """Обновить рейс."""
        flight = flight_crud.get_flight(self.db, flight_id)
        if not flight:
            raise ValueError("Рейс не найден")

        return flight_crud.update_flight(self.db, flight, payload)

    def delete_flight(self, flight_id: int) -> dict:
        """Удалить рейс с проверкой зависимостей."""
        flight = flight_crud.get_flight(self.db, flight_id)
        if not flight:
            raise ValueError("Рейс не найден")

        tickets_count = flight_crud.count_flight_tickets(self.db, flight_id)

        if tickets_count > 0:
            raise ValueError(f"Нельзя удалить рейс: {tickets_count} проданных билетов")

        return flight_crud.delete_flight(self.db, flight)

    def search_flights(self, criteria: FlightSearch) -> list[Flight]:
        """Поиск рейсов."""
        return flight_crud.search_flights(self.db, criteria)

    def get_upcoming_flights(self, skip: int = 0, limit: int = 100) -> list[Flight]:
        """Получить ближайшие рейсы."""
        return flight_crud.get_upcoming_flights(self.db, skip, limit)

    def get_flights_by_airport(
        self, airport_id: int, is_departure: bool = True
    ) -> list[Flight]:
        """Получить рейсы из/в аэропорт."""
        return flight_crud.get_flights_by_airport(self.db, airport_id, is_departure)

    # =========================================================
    # FLIGHT PRICE
    # =========================================================

    def get_flight_price(self, price_id: int):
        """Получить цену по ID."""
        return flight_crud.get_flight_price(self.db, price_id)

    def get_flight_prices_by_flight(self, flight_id: int):
        """Получить все цены на рейс."""
        return flight_crud.get_flight_prices_by_flight(self.db, flight_id)

    def create_flight_price(self, payload):
        """Создать цену на рейс."""
        flight = flight_crud.get_flight(self.db, payload.id_flight)
        if not flight:
            raise ValueError("Рейс не найден")

        from app.models import SeatClass

        seat_class = self.db.get(SeatClass, payload.id_seat_class)
        if not seat_class:
            raise ValueError("Класс мест не найден")

        return flight_crud.create_flight_price(self.db, payload)

    def update_flight_price(self, price_id: int, new_price: float):
        """Обновить цену на рейс."""
        price = flight_crud.get_flight_price(self.db, price_id)
        if not price:
            raise ValueError("Цена не найдена")

        return flight_crud.update_flight_price(self.db, price, new_price)

    def delete_flight_price(self, price_id: int) -> dict:
        """Удалить цену на рейс."""
        price = flight_crud.get_flight_price(self.db, price_id)
        if not price:
            raise ValueError("Цена не найдена")

        return flight_crud.delete_flight_price(self.db, price)
