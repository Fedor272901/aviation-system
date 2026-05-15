"""CRUD операции для сущностей Flight (рейсы).

Отвечает только за работу с базой данных (SELECT, INSERT, UPDATE, DELETE).
Бизнес-логика находится в services/.
"""

from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_
from datetime import datetime
from app.models import (
    Airport,
    Airline,
    FlightStatus,
    Flight,
    FlightPrice,
    ModelAircraft,
)
from app.schemas.flight import (
    AirportCreate,
    AirlineCreate,
    FlightStatusCreate,
    FlightCreate,
    FlightUpdate,
    FlightPriceCreate,
    FlightSearch,
)
import logging

logger = logging.getLogger(__name__)


# =========================================================
# AIRPORT
# =========================================================


def get_airport(db: Session, airport_id: int) -> Airport | None:
    """Получить аэропорт по ID."""
    return db.get(Airport, airport_id)


def get_airport_by_code(db: Session, code: str) -> Airport | None:
    """Получить аэропорт по коду (IATA)."""
    return db.scalar(select(Airport).where(Airport.code == code.upper()))


def get_all_airports(db: Session) -> list[Airport]:
    """Получить все аэропорты."""
    return db.execute(select(Airport).order_by(Airport.code)).scalars().all()


def create_airport(db: Session, payload: AirportCreate) -> Airport:
    """Создать новый аэропорт."""
    # Проверка на уникальность кода
    existing = get_airport_by_code(db, payload.code)
    if existing:
        raise ValueError(f"Аэропорт с кодом '{payload.code}' уже существует")

    airport = Airport(
        code=payload.code.upper(),
        name=payload.name,
        city=payload.city,
    )
    db.add(airport)
    db.commit()
    db.refresh(airport)

    logger.info(f"Создан аэропорт: {airport.code} ({airport.city}) (id={airport.id})")
    return airport


def update_airport(db: Session, airport: Airport, payload: AirportCreate) -> Airport:
    """Обновить данные аэропорта."""
    # Проверка на уникальность кода (если изменён)
    if payload.code.upper() != airport.code:
        existing = get_airport_by_code(db, payload.code)
        if existing:
            raise ValueError(f"Аэропорт с кодом '{payload.code}' уже существует")
        airport.code = payload.code.upper()

    airport.name = payload.name
    airport.city = payload.city
    db.commit()
    db.refresh(airport)

    logger.info(f"Обновлен аэропорт: {airport.code} (id={airport.id})")
    return airport


def delete_airport(db: Session, airport: Airport) -> dict:
    """Удалить аэропорт."""
    airport_id = airport.id
    airport_code = airport.code

    # Проверка: есть ли рейсы с этим аэропортом
    departing_count = db.execute(
        select(Flight).where(Flight.id_from == airport_id)
    ).count()
    arriving_count = db.execute(
        select(Flight).where(Flight.id_to == airport_id)
    ).count()

    if departing_count > 0 or arriving_count > 0:
        raise ValueError(
            f"Нельзя удалить аэропорт: есть {departing_count} вылетающих и "
            f"{arriving_count} прибывающих рейсов"
        )

    logger.info(f"Удален аэропорт: {airport_code} (id={airport_id})")

    db.delete(airport)
    db.commit()

    return {
        "message": "Аэропорт успешно удален",
        "deleted_id": airport_id,
        "deleted_code": airport_code,
    }


# =========================================================
# AIRLINE
# =========================================================


def get_airline(db: Session, airline_id: int) -> Airline | None:
    """Получить авиакомпанию по ID."""
    return db.get(Airline, airline_id)


def get_airline_by_code(db: Session, code: str) -> Airline | None:
    """Получить авиакомпанию по коду (IATA)."""
    return db.scalar(select(Airline).where(Airline.code == code.upper()))


def get_all_airlines(db: Session) -> list[Airline]:
    """Получить все авиакомпании."""
    return db.execute(select(Airline).order_by(Airline.name)).scalars().all()


def create_airline(db: Session, payload: AirlineCreate) -> Airline:
    """Создать новую авиакомпанию."""
    # Проверка на уникальность кода
    existing = get_airline_by_code(db, payload.code)
    if existing:
        raise ValueError(f"Авиакомпания с кодом '{payload.code}' уже существует")

    airline = Airline(
        name=payload.name,
        code=payload.code.upper(),
        country=payload.country,
    )
    db.add(airline)
    db.commit()
    db.refresh(airline)

    logger.info(f"Создана авиакомпания: {airline.name} (id={airline.id})")
    return airline


def update_airline(db: Session, airline: Airline, payload: AirlineCreate) -> Airline:
    """Обновить данные авиакомпании."""
    # Проверка на уникальность кода (если изменён)
    if payload.code.upper() != airline.code:
        existing = get_airline_by_code(db, payload.code)
        if existing:
            raise ValueError(f"Авиакомпания с кодом '{payload.code}' уже существует")
        airline.code = payload.code.upper()

    airline.name = payload.name
    airline.country = payload.country
    db.commit()
    db.refresh(airline)

    logger.info(f"Обновлена авиакомпания: {airline.name} (id={airline.id})")
    return airline


def delete_airline(db: Session, airline: Airline) -> dict:
    """Удалить авиакомпанию."""
    airline_id = airline.id
    airline_name = airline.name

    # Проверка: есть ли рейсы у этой авиакомпании
    flights_count = db.execute(
        select(Flight).where(Flight.id_airline == airline_id)
    ).count()

    if flights_count > 0:
        raise ValueError(
            f"Нельзя удалить авиакомпанию: есть {flights_count} рейсов"
        )

    logger.info(f"Удалена авиакомпания: {airline_name} (id={airline_id})")

    db.delete(airline)
    db.commit()

    return {
        "message": "Авиакомпания успешно удалена",
        "deleted_id": airline_id,
        "deleted_name": airline_name,
    }


# =========================================================
# FLIGHT STATUS
# =========================================================


def get_flight_status(db: Session, status_id: int) -> FlightStatus | None:
    """Получить статус по ID."""
    return db.get(FlightStatus, status_id)


def get_flight_status_by_name(
    db: Session, status_name: str
) -> FlightStatus | None:
    """Получить статус по имени."""
    return db.scalar(
        select(FlightStatus).where(FlightStatus.status_name == status_name)
    )


def get_all_flight_statuses(db: Session) -> list[FlightStatus]:
    """Получить все статусы."""
    return db.execute(
        select(FlightStatus).order_by(FlightStatus.id)
    ).scalars().all()


def create_flight_status(db: Session, payload: FlightStatusCreate) -> FlightStatus:
    """Создать новый статус."""
    # Проверка на уникальность
    existing = get_flight_status_by_name(db, payload.status_name)
    if existing:
        raise ValueError(f"Статус '{payload.status_name}' уже существует")

    status = FlightStatus(status_name=payload.status_name)
    db.add(status)
    db.commit()
    db.refresh(status)

    logger.info(f"Создан статус: {status.status_name} (id={status.id})")
    return status


def delete_flight_status(db: Session, status: FlightStatus) -> dict:
    """Удалить статус."""
    status_id = status.id
    status_name = status.status_name

    # Проверка: есть ли рейсы с этим статусом
    flights_count = db.execute(
        select(Flight).where(Flight.id_status == status_id)
    ).count()

    if flights_count > 0:
        raise ValueError(
            f"Нельзя удалить статус: {flights_count} рейсов используют этот статус"
        )

    logger.info(f"Удален статус: {status_name} (id={status_id})")

    db.delete(status)
    db.commit()

    return {
        "message": "Статус успешно удален",
        "deleted_id": status_id,
        "deleted_name": status_name,
    }


# =========================================================
# FLIGHT
# =========================================================


def get_flight(db: Session, flight_id: int) -> Flight | None:
    """Получить рейс по ID."""
    return db.get(Flight, flight_id)


def get_flight_by_number(db: Session, flight_number: str) -> Flight | None:
    """Получить рейс по номеру."""
    return db.scalar(
        select(Flight).where(Flight.flight_number == flight_number)
    )


def get_all_flights(
    db: Session, skip: int = 0, limit: int = 100
) -> list[Flight]:
    """Получить все рейсы с пагинацией."""
    return (
        db.execute(
            select(Flight).order_by(Flight.departure_datetime).offset(skip).limit(limit)
        )
        .scalars()
        .all()
    )


def search_flights(db: Session, criteria: FlightSearch) -> list[Flight]:
    """Поиск рейсов по критериям."""
    query = select(Flight)

    if criteria.id_from:
        query = query.where(Flight.id_from == criteria.id_from)

    if criteria.id_to:
        query = query.where(Flight.id_to == criteria.id_to)

    if criteria.date_from:
        query = query.where(Flight.departure_datetime >= criteria.date_from)

    if criteria.date_to:
        query = query.where(Flight.departure_datetime <= criteria.date_to)

    if criteria.id_airline:
        query = query.where(Flight.id_airline == criteria.id_airline)

    query = query.order_by(Flight.departure_datetime)

    return db.execute(query).scalars().all()


def get_upcoming_flights(
    db: Session, skip: int = 0, limit: int = 100
) -> list[Flight]:
    """Получить ближайшие рейсы (из будущего)."""
    now = datetime.now()
    return (
        db.execute(
            select(Flight)
            .where(Flight.departure_datetime >= now)
            .order_by(Flight.departure_datetime)
            .offset(skip)
            .limit(limit)
        )
        .scalars()
        .all()
    )


def get_flights_by_airport(
    db: Session, airport_id: int, is_departure: bool = True
) -> list[Flight]:
    """Получить все рейсы из/в аэропорт."""
    if is_departure:
        return (
            db.execute(
                select(Flight)
                .where(Flight.id_from == airport_id)
                .order_by(Flight.departure_datetime)
            )
            .scalars()
            .all()
        )
    else:
        return (
            db.execute(
                select(Flight)
                .where(Flight.id_to == airport_id)
                .order_by(Flight.departure_datetime)
            )
            .scalars()
            .all()
        )


def create_flight(db: Session, payload: FlightCreate) -> Flight:
    """Создать новый рейс."""
    # Проверка существования сущностей
    from_airport = db.get(Airport, payload.id_from)
    if not from_airport:
        raise ValueError("Аэропорт вылета не найден")

    to_airport = db.get(Airport, payload.id_to)
    if not to_airport:
        raise ValueError("Аэропорт прилёта не найден")

    if payload.id_from == payload.id_to:
        raise ValueError("Аэропорт вылета и прилёта не могут совпадать")

    airline = db.get(Airline, payload.id_airline)
    if not airline:
        raise ValueError("Авиакомпания не найдена")

    aircraft = db.get(ModelAircraft, payload.id_aircraft)
    if not aircraft:
        raise ValueError("Самолёт не найден")

    status = db.get(FlightStatus, payload.id_status)
    if not status:
        raise ValueError("Статус рейса не найден")

    # Проверка: время прилёта должно быть после вылета
    if payload.arrival_datetime <= payload.departure_datetime:
        raise ValueError("Время прилёта должно быть после времени вылета")

    # Проверка: рейс не должен быть в прошлом
    if payload.departure_datetime < datetime.now():
        raise ValueError("Невозможно создать рейс в прошлом")

    flight = Flight(
        flight_number=payload.flight_number,
        departure_datetime=payload.departure_datetime,
        arrival_datetime=payload.arrival_datetime,
        id_from=payload.id_from,
        id_to=payload.id_to,
        id_airline=payload.id_airline,
        id_aircraft=payload.id_aircraft,
        id_status=payload.id_status,
    )

    db.add(flight)
    db.commit()
    db.refresh(flight)

    logger.info(
        f"Создан рейс: {flight.flight_number} "
        f"({from_airport.code} -> {to_airport.code}) (id={flight.id})"
    )
    return flight


def update_flight(db: Session, flight: Flight, payload: FlightUpdate) -> Flight:
    """Обновить данные рейса."""
    update_data = payload.model_dump(exclude_unset=True)

    if update_data:
        for field, value in update_data.items():
            setattr(flight, field, value)

    db.commit()
    db.refresh(flight)

    logger.info(f"Обновлен рейс: {flight.flight_number} (id={flight.id})")
    return flight


def delete_flight(db: Session, flight: Flight) -> dict:
    """Удалить рейс."""
    flight_id = flight.id
    flight_number = flight.flight_number

    # Проверка: есть ли билеты на этот рейс
    from app.models import Ticket

    tickets_count = db.execute(
        select(Ticket).where(Ticket.id_flight == flight_id)
    ).count()

    if tickets_count > 0:
        raise ValueError(
            f"Нельзя удалить рейс: {tickets_count} проданных билетов"
        )

    logger.info(f"Удален рейс: {flight_number} (id={flight_id})")

    db.delete(flight)
    db.commit()

    return {
        "message": "Рейс успешно удален",
        "deleted_id": flight_id,
        "flight_number": flight_number,
    }


# =========================================================
# FLIGHT PRICE
# =========================================================


def get_flight_price(db: Session, price_id: int) -> FlightPrice | None:
    """Получить цену по ID."""
    return db.get(FlightPrice, price_id)


def get_flight_prices_by_flight(
    db: Session, flight_id: int
) -> list[FlightPrice]:
    """Получить все цены на рейс."""
    return (
        db.execute(
            select(FlightPrice)
            .where(FlightPrice.id_flight == flight_id)
            .order_by(FlightPrice.id_seat_class)
        )
        .scalars()
        .all()
    )


def get_active_flight_price(
    db: Session, flight_id: int, seat_class_id: int
) -> FlightPrice | None:
    """Получить активную цену на рейс для класса мест."""
    from datetime import datetime

    now = datetime.now()

    return db.scalar(
        select(FlightPrice)
        .where(
            FlightPrice.id_flight == flight_id,
            FlightPrice.id_seat_class == seat_class_id,
            or_(
                FlightPrice.valid_to == None,
                FlightPrice.valid_to >= now,
            ),
        )
        .order_by(FlightPrice.valid_from.desc())
    )


def create_flight_price(db: Session, payload: FlightPriceCreate) -> FlightPrice:
    """Создать цену на рейс."""
    # Проверка существования сущностей
    flight = db.get(Flight, payload.id_flight)
    if not flight:
        raise ValueError("Рейс не найден")

    from app.models import SeatClass

    seat_class = db.get(SeatClass, payload.id_seat_class)
    if not seat_class:
        raise ValueError("Класс мест не найден")

    # Проверка: цена уже существует для этой даты
    now = datetime.now()
    valid_from = payload.valid_from or now

    existing = db.scalar(
        select(FlightPrice)
        .where(
            FlightPrice.id_flight == payload.id_flight,
            FlightPrice.id_seat_class == payload.id_seat_class,
            FlightPrice.valid_from == valid_from,
        )
    )

    if existing:
        raise ValueError("Цена для этого рейса и класса уже существует на эту дату")

    price = FlightPrice(
        id_flight=payload.id_flight,
        id_seat_class=payload.id_seat_class,
        price=payload.price,
        valid_from=payload.valid_from or now,
        valid_to=payload.valid_to,
    )

    db.add(price)
    db.commit()
    db.refresh(price)

    logger.info(
        f"Создана цена: рейс={price.id_flight}, "
        f"класс={price.id_seat_class}, цена={price.price}"
    )
    return price


def update_flight_price(
    db: Session, price: FlightPrice, new_price: float
) -> FlightPrice:
    """Обновить цену на рейс."""
    price.price = new_price
    db.commit()
    db.refresh(price)

    logger.info(f"Обновлена цена: id={price.id}, новая цена={new_price}")
    return price


def delete_flight_price(db: Session, price: FlightPrice) -> dict:
    """Удалить цену на рейс."""
    price_id = price.id
    flight_id = price.id_flight

    logger.info(f"Удалена цена: id={price_id}, рейс={flight_id}")

    db.delete(price)
    db.commit()

    return {
        "message": "Цена успешно удалена",
        "deleted_id": price_id,
        "flight_id": flight_id,
    }