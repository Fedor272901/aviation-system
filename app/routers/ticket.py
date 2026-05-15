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
from app import crud
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


# =========================================================
# TICKET STATUSES
# =========================================================


@router.get("/statuses/", response_model=List[TicketStatusRead])
def list_ticket_statuses(db: Session = Depends(get_db)):
    """Получить все статусы билетов."""
    return crud.ticket.get_all_ticket_statuses(db)


@router.get("/statuses/{status_id}", response_model=TicketStatusRead)
def get_ticket_status(status_id: int, db: Session = Depends(get_db)):
    """Получить статус билета по ID."""
    status = crud.ticket.get_ticket_status(db, status_id)
    if not status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Статус не найден"
        )
    return status


@router.post(
    "/statuses/",
    response_model=TicketStatusRead,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket_status(payload: TicketStatusCreate, db: Session = Depends(get_db)):
    """Создать новый статус билета."""
    try:
        return crud.ticket.create_ticket_status(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/statuses/{status_id}", response_model=DeleteResponse)
def delete_ticket_status(status_id: int, db: Session = Depends(get_db)):
    """Удалить статус билета."""
    status = crud.ticket.get_ticket_status(db, status_id)
    if not status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Статус не найден"
        )

    try:
        return crud.ticket.delete_ticket_status(db, status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка при удалении: {str(e)}"
        )


# =========================================================
# TICKETS
# =========================================================


@router.get("/", response_model=List[TicketRead])
def list_tickets(
    skip: int = Query(0, ge=0, description="Пропустить N записей"),
    limit: int = Query(100, ge=1, le=1000, description="Максимум записей"),
    db: Session = Depends(get_db),
):
    """Получить все билеты с пагинацией."""
    return crud.ticket.get_all_tickets(db, skip=skip, limit=limit)


@router.get("/{ticket_id}", response_model=TicketRead)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """Получить билет по ID."""
    ticket = crud.ticket.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Билет не найден"
        )
    return ticket


@router.post(
    "/",
    response_model=TicketRead,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket(payload: TicketCreate, db: Session = Depends(get_db)):
    """Купить билет."""
    try:
        return crud.ticket.create_ticket(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{ticket_id}", response_model=TicketRead)
def update_ticket(
    ticket_id: int, payload: TicketUpdate, db: Session = Depends(get_db)
):
    """Обновить данные билета."""
    ticket = crud.ticket.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Билет не найден"
        )

    try:
        return crud.ticket.update_ticket(db, ticket, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{ticket_id}", response_model=DeleteResponse)
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """Удалить билет."""
    ticket = crud.ticket.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Билет не найден"
        )

    try:
        return crud.ticket.delete_ticket(db, ticket)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка при удалении: {str(e)}"
        )


# =========================================================
# TICKET SEARCH
# =========================================================


@router.post(
    "/search/",
    response_model=List[TicketRead],
    summary="Поиск билетов",
)
def search_tickets(criteria: TicketSearch, db: Session = Depends(get_db)):
    """
    Поиск билетов по критериям.

    Можно искать по:
    - пассажиру
    - рейсу
    - статусу
    - дате покупки
    """
    return crud.ticket.search_tickets(db, criteria)


@router.get(
    "/passenger/{passenger_id}/",
    response_model=List[TicketRead],
)
def get_passenger_tickets(
    passenger_id: int,
    db: Session = Depends(get_db),
):
    """Получить все билеты пассажира."""
    return crud.ticket.get_tickets_by_passenger(db, passenger_id)


@router.get(
    "/flight/{flight_id}/",
    response_model=List[TicketRead],
)
def get_flight_tickets(
    flight_id: int,
    db: Session = Depends(get_db),
):
    """Получить все билеты на рейс."""
    return crud.ticket.get_tickets_by_flight(db, flight_id)


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
    try:
        return crud.ticket.get_available_seats_for_flight(
            db, flight_id, seat_class_id
        )
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
def cancel_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """
    Отменить билет.

    Изменяет статус билета на "Отменён".
    """
    ticket = crud.ticket.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Билет не найден"
        )

    try:
        return crud.ticket.cancel_ticket(db, ticket)
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
    return crud.ticket.get_ticket_statistics(db)