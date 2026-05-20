"""HTTP эндпоинты для управления билетами (Ticket).

Включает:
- CRUD для TicketStatus (статусы билетов)
- CRUD для Ticket (билеты)
- Поиск билетов
- Статистика
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from decimal import Decimal

from app.dependencies import get_db
from app.dependencies.auth import get_current_user, require_admin
from app.models import Person
from app.services.ticket import TicketService
from app.schemas.ticket import (
    TicketStatusCreate,
    TicketStatusRead,
    TicketCreate,
    TicketUpdate,
    TicketRead,
    TicketSearch,
    DeleteResponse,
)

router = APIRouter(prefix="/tickets", tags=["Ticket"])


def _check_self_or_admin(current_user: Person, target_id: int) -> None:
    user_roles = {r.role.role_name for r in current_user.system_roles}
    if current_user.id != target_id and "admin" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к данному ресурсу",
        )


def _check_ticket_owner_or_admin(current_user: Person, ticket) -> None:
    user_roles = {r.role.role_name for r in current_user.system_roles}
    if current_user.id != ticket.id_passenger and "admin" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к данному билету",
        )


# =========================================================
# TICKET STATUSES
# =========================================================


@router.get("/statuses/", response_model=List[TicketStatusRead])
def list_ticket_statuses(db: Session = Depends(get_db)):
    """Получить все статусы билетов."""
    service = TicketService(db)
    return service.get_all_ticket_statuses()


@router.get("/statuses/{status_id}", response_model=TicketStatusRead)
def get_ticket_status(status_id: int, db: Session = Depends(get_db)):
    """Получить статус билета по ID."""
    service = TicketService(db)
    status_ticket = service.get_ticket_status(status_id)
    if not status_ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Статус не найден"
        )
    return status_ticket


@router.post(
    "/statuses/",
    response_model=TicketStatusRead,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket_status(
    payload: TicketStatusCreate,
    db: Session = Depends(get_db),
    current_user: Person = Depends(require_admin),
):
    """Создать новый статус билета."""
    service = TicketService(db)
    try:
        return service.create_ticket_status(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/statuses/{status_id}", response_model=DeleteResponse)
def delete_ticket_status(
    status_id: int,
    db: Session = Depends(get_db),
    current_user: Person = Depends(require_admin),
):
    """Удалить статус билета."""
    service = TicketService(db)
    try:
        return service.delete_ticket_status(status_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении: {str(e)}")


# =========================================================
# TICKETS
# =========================================================


@router.get("/", response_model=List[TicketRead])
def list_tickets(
    skip: int = Query(0, ge=0, description="Пропустить N записей"),
    limit: int = Query(100, ge=1, le=1000, description="Максимум записей"),
    db: Session = Depends(get_db),
    current_user: Person = Depends(require_admin),
):
    """Получить все билеты с пагинацией."""
    service = TicketService(db)
    return service.get_all_tickets(skip=skip, limit=limit)


@router.get("/{ticket_id}", response_model=TicketRead)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: Person = Depends(get_current_user),
):
    """Получить билет по ID. Доступно владельцу или админу."""

    service = TicketService(db)
    ticket = service.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Билет не найден"
        )
    _check_ticket_owner_or_admin(current_user, ticket)
    return ticket


@router.post(
    "/",
    response_model=TicketRead,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket(
    payload: TicketCreate,
    db: Session = Depends(get_db),
    current_user: Person = Depends(get_current_user),
):
    """Купить билет (требуется авторизация)."""
    _check_self_or_admin(current_user, payload.id_passenger)

    service = TicketService(db)
    try:
        return service.create_ticket(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{ticket_id}", response_model=TicketRead)
def update_ticket(
    ticket_id: int,
    payload: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: Person = Depends(require_admin),
):
    """Обновить данные билета (только админ)."""
    service = TicketService(db)
    try:
        return service.update_ticket(ticket_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{ticket_id}", response_model=DeleteResponse)
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: Person = Depends(require_admin),
):
    """Удалить билет (только админ)."""
    service = TicketService(db)
    try:
        return service.delete_ticket(ticket_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении: {str(e)}")


# def create_ticket(payload: TicketCreate, db: Session = Depends(get_db)):
#     """Купить билет."""
#     service = TicketService(db)
#     try:
#         return service.create_ticket(payload)
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @router.put("/{ticket_id}", response_model=TicketRead)
# def update_ticket(ticket_id: int, payload: TicketUpdate, db: Session = Depends(get_db)):
#     """Обновить данные билета."""
#     service = TicketService(db)
#     try:
#         return service.update_ticket(ticket_id, payload)
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @router.delete("/{ticket_id}", response_model=DeleteResponse)
# def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
#     """Удалить билет."""
#     service = TicketService(db)
#     try:
#         return service.delete_ticket(ticket_id)
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Ошибка при удалении: {str(e)}")


# =========================================================
# TICKET SEARCH
# =========================================================


@router.post(
    "/search/",
    response_model=List[TicketRead],
    summary="Поиск билетов",
)
def search_tickets(
    criteria: TicketSearch,
    db: Session = Depends(get_db),
    current_user: Person = Depends(require_admin),
):
    """
    Поиск билетов по критериям.

    Можно искать по:
    - пассажиру
    - рейсу
    - статусу
    - дате покупки
    """
    service = TicketService(db)
    return service.search_tickets(criteria)


@router.get(
    "/passenger/{passenger_id}/",
    response_model=List[TicketRead],
)
def get_passenger_tickets(
    passenger_id: int,
    db: Session = Depends(get_db),
    current_user: Person = Depends(get_current_user),
):
    """Получить все билеты пассажира. Доступно самому пассажиру или админу."""

    _check_self_or_admin(current_user, passenger_id)
    service = TicketService(db)
    return service.get_tickets_by_passenger(passenger_id)


@router.get(
    "/flight/{flight_id}/",
    response_model=List[TicketRead],
)
def get_flight_tickets(
    flight_id: int,
    db: Session = Depends(get_db),
):
    """Получить все билеты на рейс."""
    service = TicketService(db)
    return service.get_tickets_by_flight(flight_id)


@router.get(
    "/flight/{flight_id}/available/",
    response_model=List[str],
)
def get_available_seats(
    flight_id: int,
    seat_class_id: int = Query(..., description="ID класса мест"),
    db: Session = Depends(get_db),
):
    """Получить список свободных мест для рейса и класса."""
    service = TicketService(db)
    try:
        return service.get_available_seats_for_flight(flight_id, seat_class_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# =========================================================
# TICKET ACTIONS
# =========================================================


@router.post(
    "/{ticket_id}/cancel/",
    response_model=TicketRead,
    summary="Отменить билет",
)
def cancel_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: Person = Depends(get_current_user),
):
    """
    Отменить билет. Доступно владельцу или админу.

    Изменяет статус билета на "Отменён".
    Требуется авторизация.
    """

    service = TicketService(db)
    ticket = service.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Билет не найден"
        )
    _check_ticket_owner_or_admin(current_user, ticket)

    try:
        return service.cancel_ticket(ticket_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# =========================================================
# STATISTICS
# =========================================================


@router.get(
    "/statistics/",
    summary="Статистика по билетам",
)
def get_ticket_statistics(db: Session = Depends(get_db)):
    """Получить статистику по всем билетам."""
    from backend.app.crud import ticket as ticket_crud

    return ticket_crud.get_ticket_statistics(db)
