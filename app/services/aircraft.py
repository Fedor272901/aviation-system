"""Сервисный слой для сущностей Aircraft."""

from sqlalchemy.orm import Session
from app.crud import aircraft as aircraft_crud
from app.models import SeatClass, ModelAircraft, ModelSeat, Aircraft, AircraftLease
from app.schemas.aircraft import (
    SeatClassCreate,
    ModelAircraftCreate,
    AircraftCreate,
    AircraftLeaseCreate,
)
from datetime import date
import logging

logger = logging.getLogger(__name__)


class AircraftService:
    """Сервис для работы с самолётами."""

    def __init__(self, db: Session):
        self.db = db

    # =========================================================
    # SEAT CLASS
    # =========================================================

    def get_seat_class(self, class_id: int) -> SeatClass | None:
        """Получить класс мест по ID."""
        return aircraft_crud.get_seat_class(self.db, class_id)

    def get_all_seat_classes(self) -> list[SeatClass]:
        """Получить все классы мест."""
        return aircraft_crud.get_all_seat_classes(self.db)

    def create_seat_class(self, payload: SeatClassCreate) -> SeatClass:
        """Создать класс мест с проверкой уникальности."""
        if aircraft_crud.get_seat_class_by_name(self.db, payload.class_name):
            raise ValueError(f"Класс мест '{payload.class_name}' уже существует")
        return aircraft_crud.create_seat_class(self.db, payload)

    def update_seat_class(self, class_id: int, payload: SeatClassCreate) -> SeatClass:
        """Обновить класс мест с проверкой уникальности."""
        seat_class = aircraft_crud.get_seat_class(self.db, class_id)
        if not seat_class:
            raise ValueError("Класс мест не найден")

        if payload.class_name != seat_class.class_name:
            if aircraft_crud.get_seat_class_by_name(self.db, payload.class_name):
                raise ValueError(f"Класс мест '{payload.class_name}' уже существует")

        return aircraft_crud.update_seat_class(self.db, seat_class, payload)

    def delete_seat_class(self, class_id: int) -> dict:
        """Удалить класс мест с проверкой зависимостей."""
        seat_class = aircraft_crud.get_seat_class(self.db, class_id)
        if not seat_class:
            raise ValueError("Класс мест не найден")

        model_seats_count = aircraft_crud.count_seat_class_model_seats(
            self.db, class_id
        )

        if model_seats_count > 0:
            raise ValueError(
                f"Нельзя удалить класс: {model_seats_count} распределений мест используют его"
            )

        return aircraft_crud.delete_seat_class(self.db, seat_class)

    # =========================================================
    # MODEL AIRCRAFT
    # =========================================================

    def get_model_aircraft(self, model_id: int) -> ModelAircraft | None:
        """Получить модель самолёта по ID."""
        return aircraft_crud.get_model_aircraft(self.db, model_id)

    def get_all_model_aircraft(self) -> list[ModelAircraft]:
        """Получить все модели самолётов."""
        return aircraft_crud.get_all_model_aircraft(self.db)

    def create_model_aircraft(self, payload: ModelAircraftCreate) -> ModelAircraft:
        """Создать модель самолёта."""
        return aircraft_crud.create_model_aircraft(self.db, payload)

    def update_model_aircraft(self, model_id: int, payload: ModelAircraftCreate) -> ModelAircraft:
        """Обновить модель самолёта."""
        model = aircraft_crud.get_model_aircraft(self.db, model_id)
        if not model:
            raise ValueError("Модель не найдена")

        return aircraft_crud.update_model_aircraft(self.db, model, payload)

    def delete_model_aircraft(self, model_id: int) -> dict:
        """Удалить модель с проверкой зависимостей."""
        model = aircraft_crud.get_model_aircraft(self.db, model_id)
        if not model:
            raise ValueError("Модель не найдена")

        aircraft_count = aircraft_crud.count_model_aircraft(self.db, model_id)

        if aircraft_count > 0:
            raise ValueError(
                f"Нельзя удалить модель: {aircraft_count} самолётов используют её"
            )

        model_seats_count = aircraft_crud.count_model_model_seats(self.db, model_id)

        if model_seats_count > 0:
            raise ValueError(
                f"Нельзя удалить модель: {model_seats_count} распределений мест"
            )

        return aircraft_crud.delete_model_aircraft(self.db, model)

    # =========================================================
    # AIRCRAFT
    # =========================================================

    def get_aircraft(self, aircraft_id: int) -> Aircraft | None:
        """Получить самолёт по ID."""
        return aircraft_crud.get_aircraft(self.db, aircraft_id)

    def get_all_aircraft(self, skip: int = 0, limit: int = 100) -> list[Aircraft]:
        """Получить все самолёты с пагинацией."""
        return aircraft_crud.get_all_aircraft(self.db, skip, limit)

    def create_aircraft(self, payload: AircraftCreate) -> Aircraft:
        """Создать самолёт с проверкой уникальности."""
        if aircraft_crud.get_aircraft_by_registration(self.db, payload.registration_number):
            raise ValueError(
                f"Самолёт с номером '{payload.registration_number}' уже существует"
            )

        model = aircraft_crud.get_model_aircraft(self.db, payload.id_model)
        if not model:
            raise ValueError("Модель самолёта не найдена")

        return aircraft_crud.create_aircraft(self.db, payload)

    def update_aircraft(self, aircraft_id: int, payload) -> Aircraft:
        """Обновить самолёт с проверкой уникальности."""
        aircraft = aircraft_crud.get_aircraft(self.db, aircraft_id)
        if not aircraft:
            raise ValueError("Самолёт не найден")

        if payload.registration_number != aircraft.registration_number:
            if aircraft_crud.get_aircraft_by_registration(self.db, payload.registration_number):
                raise ValueError(
                    f"Самолёт с номером '{payload.registration_number}' уже существует"
                )

        return aircraft_crud.update_aircraft(self.db, aircraft, payload)

    def delete_aircraft(self, aircraft_id: int) -> dict:
        """Удалить самолёт с проверкой зависимостей."""
        aircraft = aircraft_crud.get_aircraft(self.db, aircraft_id)
        if not aircraft:
            raise ValueError("Самолёт не найден")

        flights_count = aircraft_crud.count_aircraft_flights(self.db, aircraft_id)

        if flights_count > 0:
            raise ValueError(
                f"Нельзя удалить самолёт: {flights_count} рейсов используют его"
            )

        leases_count = aircraft_crud.count_active_aircraft_leases(self.db, aircraft_id)

        if leases_count > 0:
            raise ValueError(
                f"Нельзя удалить самолёт: {leases_count} активных аренды"
            )

        return aircraft_crud.delete_aircraft(self.db, aircraft)

    # =========================================================
    # AIRCRAFT LEASE
    # =========================================================

    def get_aircraft_lease(self, lease_id: int) -> AircraftLease | None:
        """Получить аренду по ID."""
        return aircraft_crud.get_aircraft_lease(self.db, lease_id)

    def get_all_aircraft_leases(self) -> list[AircraftLease]:
        """Получить все аренды самолётов."""
        return aircraft_crud.get_all_aircraft_leases(self.db)

    def create_aircraft_lease(self, payload: AircraftLeaseCreate) -> AircraftLease:
        """Создать аренду с проверкой бизнес-правил."""
        aircraft = aircraft_crud.get_aircraft(self.db, payload.id_aircraft)
        if not aircraft:
            raise ValueError("Самолёт не найден")

        airline = aircraft_crud.get_airline(self.db, payload.id_airline)
        if not airline:
            raise ValueError("Авиакомпания не найдена")

        existing_active = aircraft_crud.get_active_lease_for_aircraft(
            self.db, payload.id_aircraft
        )
        if existing_active:
            raise ValueError(
                f"У самолёта уже есть активная аренда (id={existing_active.id})"
            )

        if payload.end_date and payload.end_date <= payload.start_date:
            raise ValueError("Дата окончания должна быть после даты начала")

        return aircraft_crud.create_aircraft_lease(self.db, payload)

    def update_aircraft_lease(self, lease_id: int, end_date: date) -> AircraftLease:
        """Обновить аренду."""
        lease = aircraft_crud.get_aircraft_lease(self.db, lease_id)
        if not lease:
            raise ValueError("Аренда не найдена")

        if end_date and end_date <= lease.start_date:
            raise ValueError("Дата окончания должна быть после даты начала")

        return aircraft_crud.update_aircraft_lease(self.db, lease, end_date)

    def delete_aircraft_lease(self, lease_id: int) -> dict:
        """Удалить аренду."""
        lease = aircraft_crud.get_aircraft_lease(self.db, lease_id)
        if not lease:
            raise ValueError("Аренда не найдена")

        return aircraft_crud.delete_aircraft_lease(self.db, lease)

    # =========================================================
    # MODEL SEATS
    # =========================================================

    def get_model_seat(self, seat_id: int) -> ModelSeat | None:
        """Получить распределение мест по ID."""
        return aircraft_crud.get_model_seat(self.db, seat_id)

    def get_model_seats_by_model(self, model_id: int) -> list[ModelSeat]:
        """Получить все распределения мест для модели."""
        return aircraft_crud.get_model_seats_by_model(self.db, model_id)

    def create_model_seat(self, payload: ModelSeatCreate) -> ModelSeat:
        """Создать распределение мест."""
        return aircraft_crud.create_model_seat(self.db, payload)

    def update_model_seat(self, seat_id: int, seat_count: int) -> ModelSeat:
        """Обновить количество мест."""
        model_seat = aircraft_crud.get_model_seat(self.db, seat_id)
        if not model_seat:
            raise ValueError("Распределение мест не найдено")
        return aircraft_crud.update_model_seat(self.db, model_seat, seat_count)

    def delete_model_seat(self, seat_id: int) -> dict:
        """Удалить распределение мест."""
        model_seat = aircraft_crud.get_model_seat(self.db, seat_id)
        if not model_seat:
            raise ValueError("Распределение мест не найдено")
        return aircraft_crud.delete_model_seat(self.db, model_seat)
