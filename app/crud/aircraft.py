"""CRUD операции для сущностей Aircraft (самолёты).

Отвечает только за работу с базой данных (SELECT, INSERT, UPDATE, DELETE).
Бизнес-логика находится в services/.
"""

from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import date
from app.models import (
    SeatClass,
    ModelAircraft,
    ModelSeat,
    Aircraft,
    AircraftLease,
    Airline,
)
from app.schemas.aircraft import (
    SeatClassCreate,
    ModelAircraftCreate,
    ModelSeatCreate,
    AircraftCreate,
    AircraftUpdate,
    AircraftLeaseCreate,
)
import logging

logger = logging.getLogger(__name__)


# =========================================================
# SEAT CLASS
# =========================================================


def get_seat_class(db: Session, class_id: int) -> SeatClass | None:
    """Получить класс мест по ID."""
    return db.get(SeatClass, class_id)


def get_seat_class_by_name(db: Session, class_name: str) -> SeatClass | None:
    """Получить класс мест по имени."""
    return db.scalar(
        select(SeatClass).where(SeatClass.class_name == class_name)
    )


def get_all_seat_classes(db: Session) -> list[SeatClass]:
    """Получить все классы мест."""
    return db.execute(
        select(SeatClass).order_by(SeatClass.id)
    ).scalars().all()


def create_seat_class(db: Session, payload: SeatClassCreate) -> SeatClass:
    """Создать новый класс мест."""
    # Проверка на уникальность
    existing = get_seat_class_by_name(db, payload.class_name)
    if existing:
        raise ValueError(f"Класс мест '{payload.class_name}' уже существует")

    seat_class = SeatClass(
        class_name=payload.class_name,
        price_multiplier=payload.price_multiplier,
        description=payload.description,
    )
    db.add(seat_class)
    db.commit()
    db.refresh(seat_class)

    logger.info(
        f"Создан класс мест: {seat_class.class_name} "
        f"(multiplier={seat_class.price_multiplier}) (id={seat_class.id})"
    )
    return seat_class


def update_seat_class(
    db: Session, seat_class: SeatClass, payload: SeatClassCreate
) -> SeatClass:
    """Обновить данные класса мест."""
    # Проверка на уникальность (если изменён)
    if payload.class_name != seat_class.class_name:
        existing = get_seat_class_by_name(db, payload.class_name)
        if existing:
            raise ValueError(f"Класс мест '{payload.class_name}' уже существует")
        seat_class.class_name = payload.class_name

    seat_class.price_multiplier = payload.price_multiplier
    seat_class.description = payload.description
    db.commit()
    db.refresh(seat_class)

    logger.info(f"Обновлен класс мест: {seat_class.class_name} (id={seat_class.id})")
    return seat_class


def delete_seat_class(db: Session, seat_class: SeatClass) -> dict:
    """Удалить класс мест."""
    class_id = seat_class.id
    class_name = seat_class.class_name

    # Проверка: есть ли места этого класса
    model_seats_count = db.execute(
        select(ModelSeat).where(ModelSeat.id_seat_class == class_id)
    ).count()

    if model_seats_count > 0:
        raise ValueError(
            f"Нельзя удалить класс: {model_seats_count} распределений мест используют его"
        )

    logger.info(f"Удален класс мест: {class_name} (id={class_id})")

    db.delete(seat_class)
    db.commit()

    return {
        "message": "Класс мест успешно удален",
        "deleted_id": class_id,
        "deleted_name": class_name,
    }


# =========================================================
# MODEL AIRCRAFT
# =========================================================


def get_model_aircraft(db: Session, model_id: int) -> ModelAircraft | None:
    """Получить модель самолёта по ID."""
    return db.get(ModelAircraft, model_id)


def get_all_model_aircraft(db: Session) -> list[ModelAircraft]:
    """Получить все модели самолётов."""
    return db.execute(
        select(ModelAircraft).order_by(ModelAircraft.name)
    ).scalars().all()


def create_model_aircraft(
    db: Session, payload: ModelAircraftCreate
) -> ModelAircraft:
    """Создать новую модель самолёта."""
    model = ModelAircraft(
        name=payload.name,
        manufacturer=payload.manufacturer,
    )
    db.add(model)
    db.commit()
    db.refresh(model)

    # Создаём распределение мест
    for seat_data in payload.seats:
        model_seat = ModelSeat(
            id_model=model.id,
            id_seat_class=seat_data["class_id"],
            seat_count=seat_data["count"],
        )
        db.add(model_seat)

    db.commit()
    db.refresh(model)

    logger.info(f"Создана модель самолёта: {model.name} (id={model.id})")
    return model


def update_model_aircraft(
    db: Session, model: ModelAircraft, payload: ModelAircraftBase
) -> ModelAircraft:
    """Обновить данные модели самолёта."""
    model.name = payload.name
    model.manufacturer = payload.manufacturer
    db.commit()
    db.refresh(model)

    logger.info(f"Обновлена модель самолёта: {model.name} (id={model.id})")
    return model


def delete_model_aircraft(db: Session, model: ModelAircraft) -> dict:
    """Удалить модель самолёта."""
    model_id = model.id
    model_name = model.name

    # Проверка: есть ли самолёты этой модели
    aircraft_count = db.execute(
        select(Aircraft).where(Aircraft.id_model == model_id)
    ).count()

    if aircraft_count > 0:
        raise ValueError(
            f"Нельзя удалить модель: {aircraft_count} самолётов используют её"
        )

    # Проверка: есть ли распределения мест
    model_seats_count = db.execute(
        select(ModelSeat).where(ModelSeat.id_model == model_id)
    ).count()

    if model_seats_count > 0:
        raise ValueError(
            f"Нельзя удалить модель: {model_seats_count} распределений мест"
        )

    logger.info(f"Удалена модель самолёта: {model_name} (id={model_id})")

    db.delete(model)
    db.commit()

    return {
        "message": "Модель самолёта успешно удалена",
        "deleted_id": model_id,
        "deleted_name": model_name,
    }


# =========================================================
# MODEL SEATS
# =========================================================


def get_model_seat(db: Session, seat_id: int) -> ModelSeat | None:
    """Получить распределение мест по ID."""
    return db.get(ModelSeat, seat_id)


def get_model_seats_by_model(
    db: Session, model_id: int
) -> list[ModelSeat]:
    """Получить все распределения мест для модели."""
    return (
        db.execute(
            select(ModelSeat)
            .where(ModelSeat.id_model == model_id)
            .order_by(ModelSeat.id_seat_class)
        )
        .scalars()
        .all()
    )


def get_total_seats_for_model(db: Session, model_id: int) -> int:
    """Получить общее количество мест для модели."""
    return (
        db.execute(
            select(ModelSeat)
            .where(ModelSeat.id_model == model_id)
        )
        .scalars()
        .sum()
    ) or 0


def create_model_seat(db: Session, payload: ModelSeatCreate) -> ModelSeat:
    """Создать распределение мест."""
    # Проверка существования
    model = db.get(ModelAircraft, payload.id_model)
    if not model:
        raise ValueError("Модель самолёта не найдена")

    seat_class = db.get(SeatClass, payload.id_seat_class)
    if not seat_class:
        raise ValueError("Класс мест не найден")

    # Проверка: уже есть распределение этого класса для модели
    existing = db.scalar(
        select(ModelSeat).where(
            ModelSeat.id_model == payload.id_model,
            ModelSeat.id_seat_class == payload.id_seat_class,
        )
    )
    if existing:
        raise ValueError(
            f"Распределение для класса '{seat_class.class_name}' уже существует"
        )

    model_seat = ModelSeat(
        id_model=payload.id_model,
        id_seat_class=payload.id_seat_class,
        seat_count=payload.seat_count,
    )

    db.add(model_seat)
    db.commit()
    db.refresh(model_seat)

    logger.info(
        f"Создано распределение: модель={model_seat.id_model}, "
        f"класс={model_seat.id_seat_class}, count={model_seat.seat_count}"
    )
    return model_seat


def update_model_seat(
    db: Session, model_seat: ModelSeat, seat_count: int
) -> ModelSeat:
    """Обновить количество мест."""
    model_seat.seat_count = seat_count
    db.commit()
    db.refresh(model_seat)

    logger.info(
        f"Обновлено распределение: id={model_seat.id}, count={seat_count}"
    )
    return model_seat


def delete_model_seat(db: Session, model_seat: ModelSeat) -> dict:
    """Удалить распределение мест."""
    seat_id = model_seat.id
    model_id = model_seat.id_model

    logger.info(f"Удалено распределение: id={seat_id}, модель={model_id}")

    db.delete(model_seat)
    db.commit()

    return {
        "message": "Распределение мест успешно удалено",
        "deleted_id": seat_id,
        "model_id": model_id,
    }


# =========================================================
# AIRCRAFT
# =========================================================


def get_aircraft(db: Session, aircraft_id: int) -> Aircraft | None:
    """Получить самолёт по ID."""
    return db.get(Aircraft, aircraft_id)


def get_aircraft_by_registration(
    db: Session, registration_number: str
) -> Aircraft | None:
    """Получить самолёт по регистрационному номеру."""
    return db.scalar(
        select(Aircraft).where(Aircraft.registration_number == registration_number)
    )


def get_all_aircraft(db: Session, skip: int = 0, limit: int = 100) -> list[Aircraft]:
    """Получить все самолёты с пагинацией."""
    return (
        db.execute(
            select(Aircraft).order_by(Aircraft.id).offset(skip).limit(limit)
        )
        .scalars()
        .all()
    )


def create_aircraft(db: Session, payload: AircraftCreate) -> Aircraft:
    """Создать новый самолёт."""
    # Проверка на уникальность регистрационного номера
    existing = get_aircraft_by_registration(db, payload.registration_number)
    if existing:
        raise ValueError(
            f"Самолёт с номером '{payload.registration_number}' уже существует"
        )

    # Проверка существования модели
    model = db.get(ModelAircraft, payload.id_model)
    if not model:
        raise ValueError("Модель самолёта не найдена")

    aircraft = Aircraft(
        registration_number=payload.registration_number,
        id_model=payload.id_model,
        manufacture_year=payload.manufacture_year,
        last_maintenance=payload.last_maintenance,
    )

    db.add(aircraft)
    db.commit()
    db.refresh(aircraft)

    logger.info(
        f"Создан самолёт: {aircraft.registration_number} "
        f"(модель={model.name}) (id={aircraft.id})"
    )
    return aircraft


def update_aircraft(
    db: Session, aircraft: Aircraft, payload: AircraftUpdate
) -> Aircraft:
    """Обновить данные самолёта."""
    update_data = payload.model_dump(exclude_unset=True)

    # Проверка на уникальность регистрационного номера (если изменён)
    if "registration_number" in update_data:
        if update_data["registration_number"] != aircraft.registration_number:
            existing = get_aircraft_by_registration(
                db, update_data["registration_number"]
            )
            if existing:
                raise ValueError(
                    f"Самолёт с номером '{update_data['registration_number']}' уже существует"
                )

    if update_data:
        for field, value in update_data.items():
            setattr(aircraft, field, value)

    db.commit()
    db.refresh(aircraft)

    logger.info(f"Обновлен самолёт: {aircraft.registration_number} (id={aircraft.id})")
    return aircraft


def delete_aircraft(db: Session, aircraft: Aircraft) -> dict:
    """Удалить самолёт."""
    aircraft_id = aircraft.id
    registration = aircraft.registration_number

    # Проверка: есть ли рейсы на этом самолёте
    flights_count = db.execute(
        select(aircraft.flights.__class__).where(
            aircraft.flights.__class__.id_aircraft == aircraft_id
        )
    ).count()

    if flights_count > 0:
        raise ValueError(
            f"Нельзя удалить самолёт: {flights_count} рейсов используют его"
        )

    # Проверка: есть ли активные аренды
    leases_count = db.execute(
        select(AircraftLease).where(
            AircraftLease.id_aircraft == aircraft_id,
            AircraftLease.end_date == None,
        )
    ).count()

    if leases_count > 0:
        raise ValueError(
            f"Нельзя удалить самолёт: {leases_count} активных аренды"
        )

    logger.info(f"Удален самолёт: {registration} (id={aircraft_id})")

    db.delete(aircraft)
    db.commit()

    return {
        "message": "Самолёт успешно удален",
        "deleted_id": aircraft_id,
        "registration": registration,
    }


# =========================================================
# AIRCRAFT LEASE
# =========================================================


def get_aircraft_lease(db: Session, lease_id: int) -> AircraftLease | None:
    """Получить аренду по ID."""
    return db.get(AircraftLease, lease_id)


def get_all_aircraft_leases(db: Session) -> list[AircraftLease]:
    """Получить все аренды самолётов."""
    return db.execute(
        select(AircraftLease).order_by(AircraftLease.start_date)
    ).scalars().all()


def get_active_lease_for_aircraft(
    db: Session, aircraft_id: int
) -> AircraftLease | None:
    """Получить активную аренду для самолёта."""
    from datetime import date

    return db.scalar(
        select(AircraftLease)
        .where(
            AircraftLease.id_aircraft == aircraft_id,
            AircraftLease.end_date == None,
        )
    )


def create_aircraft_lease(db: Session, payload: AircraftLeaseCreate) -> AircraftLease:
    """Создать аренду самолёта."""
    # Проверка существования
    aircraft = db.get(Aircraft, payload.id_aircraft)
    if not aircraft:
        raise ValueError("Самолёт не найден")

    airline = db.get(A airline, payload.id_airline)
    if not airline:
        raise ValueError("Авиакомпания не найдена")

    # Проверка: нет ли активной аренды
    existing_active = get_active_lease_for_aircraft(db, payload.id_aircraft)
    if existing_active:
        raise ValueError(
            f"У самолёта уже есть активная аренда (id={existing_active.id})"
        )

    # Проверка дат
    if payload.end_date and payload.end_date <= payload.start_date:
        raise ValueError("Дата окончания должна быть после даты начала")

    lease = AircraftLease(
        id_aircraft=payload.id_aircraft,
        id_airline=payload.id_airline,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )

    db.add(lease)
    db.commit()
    db.refresh(lease)

    logger.info(
        f"Создана аренда: самолёт={lease.id_aircraft}, "
        f"авиакомпания={lease.id_airline}, "
        f"с={lease.start_date}, по={lease.end_date}"
    )
    return lease


def update_aircraft_lease(
    db: Session, lease: AircraftLease, end_date: date
) -> AircraftLease:
    """Обновить дату окончания аренды."""
    if end_date and end_date <= lease.start_date:
        raise ValueError("Дата окончания должна быть после даты начала")

    lease.end_date = end_date
    db.commit()
    db.refresh(lease)

    logger.info(f"Обновлена аренда: id={lease.id}, end_date={end_date}")
    return lease


def delete_aircraft_lease(db: Session, lease: AircraftLease) -> dict:
    """Удалить аренду самолёта."""
    lease_id = lease.id
    aircraft_id = lease.id_aircraft

    logger.info(f"Удалена аренда: id={lease_id}, самолёт={aircraft_id}")

    db.delete(lease)
    db.commit()

    return {
        "message": "Аренда успешно удалена",
        "deleted_id": lease_id,
        "aircraft_id": aircraft_id,
    }