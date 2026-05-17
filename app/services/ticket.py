"""Сервисный слой для сущностей Ticket."""

from sqlalchemy.orm import Session
from app.crud import ticket as ticket_crud
from app.crud import person as person_crud
from app.models import Ticket, TicketStatus
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketSearch
import logging

logger = logging.getLogger(__name__)


class TicketService:
    """Сервис для работы с билетами."""

    def __init__(self, db: Session):
        self.db = db

    # =========================================================
    # TICKET STATUS
    # =========================================================

    def create_ticket_status(self, payload) -> TicketStatus:
        """Создать статус билета с проверкой уникальности."""
        if ticket_crud.get_ticket_status_by_name(self.db, payload.status_name):
            raise ValueError(f"Статус '{payload.status_name}' уже существует")
        return ticket_crud.create_ticket_status(self.db, payload)

    def get_ticket_status(self, status_id: int) -> TicketStatus | None:
        """Получить статус билета по ID."""
        return ticket_crud.get_ticket_status(self.db, status_id)

    def get_all_ticket_statuses(self) -> list[TicketStatus]:
        """Получить все статусы билетов."""
        return ticket_crud.get_all_ticket_statuses(self.db)

    def delete_ticket_status(self, status_id: int) -> dict:
        """Удалить статус с проверкой зависимостей."""
        status = ticket_crud.get_ticket_status(self.db, status_id)
        if not status:
            raise ValueError("Статус не найден")

        tickets_count = ticket_crud.count_status_tickets(self.db, status_id)

        if tickets_count > 0:
            raise ValueError(
                f"Нельзя удалить статус: {tickets_count} билетов используют его"
            )

        return ticket_crud.delete_ticket_status(self.db, status)

    # =========================================================
    # TICKET
    # =========================================================

    def create_ticket(self, payload: TicketCreate) -> Ticket:
        """Создать билет с проверкой бизнес-правил."""
        flight = ticket_crud.get_flight(self.db, payload.id_flight)
        if not flight:
            raise ValueError("Рейс не найден")

        seat_class = ticket_crud.get_seat_class(self.db, payload.id_seat_class)
        if not seat_class:
            raise ValueError("Класс мест не найден")

        passenger = person_crud.get_person(self.db, payload.id_passenger)
        if not passenger:
            raise ValueError("Пассажир не найден")

        # passenger = ticket_crud.get_passenger(self.db, payload.id_passenger)
        # if not passenger:
        #     raise ValueError("Пассажир не найден")

        status = ticket_crud.get_ticket_status(self.db, payload.id_status)
        if not status:
            raise ValueError("Статус билета не найден")

        if ticket_crud.check_seat_occupied(
            self.db, payload.id_flight, payload.seat_number
        ):
            raise ValueError(
                f"Место {payload.seat_number} уже занято на рейсе {flight.flight_number}"
            )

        return ticket_crud.create_ticket(self.db, payload)

    def get_ticket(self, ticket_id: int) -> Ticket | None:
        """Получить билет по ID."""
        return ticket_crud.get_ticket(self.db, ticket_id)

    def get_all_tickets(self, skip: int = 0, limit: int = 100) -> list[Ticket]:
        """Получить все билеты с пагинацией."""
        return ticket_crud.get_all_tickets(self.db, skip, limit)

    def update_ticket(self, ticket_id: int, payload: TicketUpdate) -> Ticket:
        """Обновить билет."""
        ticket = ticket_crud.get_ticket(self.db, ticket_id)
        if not ticket:
            raise ValueError("Билет не найден")

        if "seat_number" in payload.model_dump(exclude_unset=True):
            new_seat = payload.seat_number
            if new_seat != ticket.seat_number:
                if ticket_crud.check_seat_occupied(self.db, ticket.id_flight, new_seat):
                    raise ValueError(f"Место {new_seat} уже занято")

        return ticket_crud.update_ticket(self.db, ticket, payload)

    def delete_ticket(self, ticket_id: int) -> dict:
        """Удалить билет."""
        ticket = ticket_crud.get_ticket(self.db, ticket_id)
        if not ticket:
            raise ValueError("Билет не найден")

        return ticket_crud.delete_ticket(self.db, ticket)

    def cancel_ticket(self, ticket_id: int) -> Ticket:
        """Отменить билет."""
        ticket = ticket_crud.get_ticket(self.db, ticket_id)
        if not ticket:
            raise ValueError("Билет не найден")

        return ticket_crud.cancel_ticket(self.db, ticket)

    def search_tickets(self, criteria: TicketSearch) -> list[Ticket]:
        """Поиск билетов."""
        return ticket_crud.search_tickets(self.db, criteria)

    def get_tickets_by_passenger(self, passenger_id: int) -> list[Ticket]:
        """Получить все билеты пассажира."""
        return ticket_crud.get_tickets_by_passenger(self.db, passenger_id)

    def get_tickets_by_flight(self, flight_id: int) -> list[Ticket]:
        """Получить все билеты на рейс."""
        return ticket_crud.get_tickets_by_flight(self.db, flight_id)

    def get_available_seats_for_flight(
        self, flight_id: int, seat_class_id: int
    ) -> list[str]:
        """Получить список свободных мест."""
        return ticket_crud.get_available_seats_for_flight(
            self.db, flight_id, seat_class_id
        )
