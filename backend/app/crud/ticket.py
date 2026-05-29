"""CRUD операции для сущностей Ticket (билеты).

Отвечает только за работу с базой данных (SELECT, INSERT, UPDATE, DELETE).
Бизнес-логика находится в services/.
"""

from sqlalchemy.orm import Session
from sqlalchemy import select, func
from datetime import datetime
from app.models import Ticket, TicketStatus, Flight, SeatClass, Person
from app.schemas.ticket import TicketCreate, TicketStatusCreate, TicketUpdate, TicketSearch
import logging

logger = logging.getLogger(__name__)


def _get_cancelled_status_id(db: Session) -> int | None:
    """Возвращает ID статуса 'Отменён' или None, если статуса нет."""
    status = db.scalar(select(TicketStatus).where(TicketStatus.status_name == "Отменён"))
    return status.id if status else None

# =========================================================
# TICKET STATUS
# =========================================================


def get_ticket_status(db: Session, status_id: int) -> TicketStatus | None:
    """Получить статус билета по ID."""
    return db.get(TicketStatus, status_id)


def get_ticket_status_by_name(
    db: Session, status_name: str
) -> TicketStatus | None:
    """Получить статус билета по имени."""
    return db.scalar(
        select(TicketStatus).where(TicketStatus.status_name == status_name)
    )


def get_all_ticket_statuses(db: Session) -> list[TicketStatus]:
    """Получить все статусы билетов."""
    return db.execute(
        select(TicketStatus).order_by(TicketStatus.id)
    ).scalars().all()


def create_ticket_status(db: Session, payload: TicketStatusCreate) -> TicketStatus:
    """Создать новый статус билета (без проверок - только INSERT)."""
    status = TicketStatus(status_name=payload.status_name)
    db.add(status)
    db.commit()
    db.refresh(status)

    logger.info(f"Создан статус билета: {status.status_name} (id={status.id})")
    return status


def delete_ticket_status(db: Session, status: TicketStatus) -> dict:
    """Удалить статус билета (без проверок - только DELETE)."""
    status_id = status.id
    status_name = status.status_name

    logger.info(f"Удален статус билета: {status_name} (id={status_id})")

    db.delete(status)
    db.commit()

    return {
        "message": "Статус успешно удален",
        "deleted_id": status_id,
        "deleted_name": status_name,
    }


# =========================================================
# TICKET
# =========================================================


def get_ticket(db: Session, ticket_id: int) -> Ticket | None:
    """Получить билет по ID."""
    return db.get(Ticket, ticket_id)


def get_all_tickets(
    db: Session, skip: int = 0, limit: int = 100
) -> list[Ticket]:
    """Получить все билеты с пагинацией."""
    return (
        db.execute(
            select(Ticket).order_by(Ticket.purchase_date.desc()).offset(skip).limit(limit)
        )
        .scalars()
        .all()
    )


def search_tickets(db: Session, criteria: TicketSearch) -> list[Ticket]:
    """Поиск билетов по критериям."""
    query = select(Ticket)

    if criteria.id_passenger:
        query = query.where(Ticket.id_passenger == criteria.id_passenger)

    if criteria.id_flight:
        query = query.where(Ticket.id_flight == criteria.id_flight)

    if criteria.id_status:
        query = query.where(Ticket.id_status == criteria.id_status)

    if criteria.date_from:
        query = query.where(Ticket.purchase_date >= criteria.date_from)

    if criteria.date_to:
        query = query.where(Ticket.purchase_date <= criteria.date_to)

    query = query.order_by(Ticket.purchase_date.desc())

    return db.execute(query).scalars().all()


def get_tickets_by_passenger(
    db: Session, passenger_id: int
) -> list[Ticket]:
    """Получить все билеты пассажира."""
    return (
        db.execute(
            select(Ticket)
            .where(Ticket.id_passenger == passenger_id)
            .order_by(Ticket.purchase_date.desc())
        )
        .scalars()
        .all()
    )


def get_tickets_by_flight(
    db: Session, flight_id: int
) -> list[Ticket]:
    """Получить все билеты на рейс."""
    return (
        db.execute(
            select(Ticket)
            .where(Ticket.id_flight == flight_id)
            .order_by(Ticket.seat_number)
        )
        .scalars()
        .all()
    )


def get_available_seats_for_flight(
    db: Session, flight_id: int, seat_class_id: int
) -> list[str]:
    """Получить список свободных мест для рейса и класса."""
    from app.models import ModelSeat, Aircraft, ModelAircraft

    flight = db.get(Flight, flight_id)
    if not flight:
        raise ValueError("Рейс не найден")

    aircraft = db.get(Aircraft, flight.id_aircraft)
    if not aircraft:
        raise ValueError("Самолёт не найден")

    model = db.get(ModelAircraft, aircraft.id_model)
    if not model:
        raise ValueError("Модель самолёта не найдена")

    model_seat = db.scalar(
        select(ModelSeat).where(
            ModelSeat.id_model == model.id,
            ModelSeat.id_seat_class == seat_class_id,
        )
    )
    if not model_seat:
        raise ValueError("Класс мест не найден для этой модели самолёта")

    total_seats = model_seat.seat_count

    cancelled_id = _get_cancelled_status_id(db)
    query = select(Ticket.seat_number).where(
        Ticket.id_flight == flight_id,
        Ticket.id_seat_class == seat_class_id,
    )
    if cancelled_id:
        query = query.where(Ticket.id_status != cancelled_id)
    occupied_seats = db.execute(query).scalars().all()

    available = []
    for i in range(1, total_seats + 1):
        seat_letter = chr(ord('A') + (i - 1) % 3)
        seat_number = f"{i}{seat_letter}"
        if seat_number not in occupied_seats:
            available.append(seat_number)

    return available


def create_ticket(db: Session, payload: TicketCreate) -> Ticket:
    """Создать новый билет (без проверок - только INSERT)."""
    ticket = Ticket(
        seat_number=payload.seat_number,
        id_seat_class=payload.id_seat_class,
        price=payload.price,
        id_status=payload.id_status,
        id_flight=payload.id_flight,
        id_passenger=payload.id_passenger,
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    logger.info(
        f"Создан билет: id={ticket.id}, рейс={payload.id_flight}, "
        f"место={ticket.seat_number}"
    )
    return ticket


def update_ticket(db: Session, ticket: Ticket, payload: TicketUpdate) -> Ticket:
    """Обновить данные билета (без проверок - только UPDATE)."""
    update_data = payload.model_dump(exclude_unset=True)

    if update_data:
        for field, value in update_data.items():
            setattr(ticket, field, value)

    db.commit()
    db.refresh(ticket)

    logger.info(f"Обновлен билет: id={ticket.id}")
    return ticket


def cancel_ticket(db: Session, ticket: Ticket) -> Ticket:
    """Отменить билет (изменить статус на 'Отменён')."""
    cancelled_status = db.scalar(
        select(TicketStatus).where(TicketStatus.status_name == "Отменён")
    )
    if not cancelled_status:
        raise ValueError("Статус 'Отменён' не найден")

    ticket.id_status = cancelled_status.id
    db.commit()
    db.refresh(ticket)

    logger.info(f"Билет отменён: id={ticket.id}")
    return ticket


def delete_ticket(db: Session, ticket: Ticket) -> dict:
    """Удалить билет (физическое удаление из БД)."""
    ticket_id = ticket.id
    flight_number = ticket.flight.flight_number if ticket.flight else "N/A"
    seat_number = ticket.seat_number

    logger.info(f"Удален билет: id={ticket_id}, рейс={flight_number}, место={seat_number}")

    db.delete(ticket)
    db.commit()

    return {
        "message": "Билет успешно удален",
        "deleted_id": ticket_id,
        "flight_number": flight_number,
        "seat_number": seat_number,
    }


def get_ticket_statistics(db: Session) -> dict:
    """Получить статистику по билетам."""
    total = db.scalar(select(func.count()).select_from(Ticket))

    status_stats = {}
    for status in get_all_ticket_statuses(db):
        count = db.scalar(
            select(func.count()).where(Ticket.id_status == status.id)
        )
        status_stats[status.status_name] = count

    return {
        "total_tickets": total,
        "by_status": status_stats,
    }


# =========================================================
# COUNT FUNCTIONS (для сервисного слоя)
# =========================================================


def count_status_tickets(db: Session, status_id: int) -> int:
    """Получить количество билетов со статусом."""
    return db.scalar(
        select(func.count()).where(Ticket.id_status == status_id)
    ) or 0


def get_flight(db: Session, flight_id: int) -> Flight | None:
    """Получить рейс по ID."""
    return db.get(Flight, flight_id)


def get_seat_class(db: Session, seat_class_id: int) -> SeatClass | None:
    """Получить класс мест по ID."""
    return db.get(SeatClass, seat_class_id)


def get_passenger(db: Session, passenger_id: int) -> Person | None:
    """Получить пассажира по ID."""
    return db.get(Person, passenger_id)


def check_seat_occupied(
    db: Session, flight_id: int, seat_number: str
) -> bool:
    """Проверить, занято ли место на рейсе."""
    query = select(Ticket).where(
        Ticket.id_flight == flight_id,
        Ticket.seat_number == seat_number,
    )
    cancelled_id = _get_cancelled_status_id(db)
    if cancelled_id:
        query = query.where(Ticket.id_status != cancelled_id)
    existing = db.scalar(query)
    return existing is not None
