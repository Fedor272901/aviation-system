"""HTTP эндпоинты для управления рейсами (Flight).

Включает:
- CRUD для Airport (аэропорты)
- CRUD для Airline (авиакомпании)
- CRUD для FlightStatus (статусы рейсов)
- CRUD для Flight (рейсы)
- CRUD для FlightPrice (цены)
- Поиск рейсов
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from app.dependencies import get_db
from app.dependencies.auth import get_current_user, require_admin
from app.models import Person
from app.services.flight import FlightService
from app.utils.api_utils import raise_from_value_error
from app.schemas.flight import (
    AirportCreate,
    AirportRead,
    AirlineCreate,
    AirlineRead,
    FlightStatusCreate,
    FlightStatusRead,
    FlightCreate,
    FlightUpdate,
    FlightRead,
    FlightSearch,
    FlightPriceCreate,
    FlightPriceRead,
    DeleteResponse,
)

router = APIRouter(prefix="/flights", tags=["Flight"])


# =========================================================
# AIRPORTS
# =========================================================


@router.get("/airports/", response_model=List[AirportRead])
def list_airports(db: Session = Depends(get_db)):
    """Получить список всех аэропортов."""
    service = FlightService(db)
    return service.get_all_airports()


@router.get("/airports/{airport_id}", response_model=AirportRead)
def get_airport(airport_id: int, db: Session = Depends(get_db)):
    """Получить аэропорт по ID."""
    service = FlightService(db)
    airport = service.get_airport(airport_id)
    if not airport:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Аэропорт не найден"
        )
    return airport


@router.post(
    "/airports/",
    response_model=AirportRead,
    status_code=status.HTTP_201_CREATED,
)
def create_airport(
    payload: AirportCreate,
    db: Session = Depends(get_db),
    current_user: Person = Depends(require_admin),
):
    """Создать новый аэропорт."""
    service = FlightService(db)
    try:
        return service.create_airport(payload)
    except ValueError as e:
        raise_from_value_error(e)


@router.put("/airports/{airport_id}", response_model=AirportRead)
def update_airport(
    airport_id: int,
    payload: AirportCreate,
    db: Session = Depends(get_db),
    current_user: Person = Depends(require_admin),
):
    """Обновить данные аэропорта."""
    service = FlightService(db)
    try:
        return service.update_airport(airport_id, payload)
    except ValueError as e:
        raise_from_value_error(e)


@router.delete("/airports/{airport_id}", response_model=DeleteResponse)
def delete_airport(
    airport_id: int,
    db: Session = Depends(get_db),
    current_user: Person = Depends(require_admin),
):
    """Удалить аэропорт."""
    service = FlightService(db)
    try:
        return service.delete_airport(airport_id)
    except ValueError as e:
        raise_from_value_error(e)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка при удалении: {str(e)}"
        )


# =========================================================
# AIRLINES
# =========================================================


@router.get("/airlines/", response_model=List[AirlineRead])
def list_airlines(db: Session = Depends(get_db)):
    """Получить список всех авиакомпаний."""
    service = FlightService(db)
    return service.get_all_airlines()


@router.get("/airlines/{airline_id}", response_model=AirlineRead)
def get_airline(airline_id: int, db: Session = Depends(get_db)):
    """Получить авиакомпанию по ID."""
    service = FlightService(db)
    airline = service.get_airline(airline_id)
    if not airline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Авиакомпания не найдена"
        )
    return airline


@router.post(
    "/airlines/",
    response_model=AirlineRead,
    status_code=status.HTTP_201_CREATED,
)
def create_airline(
    payload: AirlineCreate,
    db: Session = Depends(get_db),
    current_user: Person = Depends(require_admin),
):
    """Создать новую авиакомпанию."""
    service = FlightService(db)
    try:
        return service.create_airline(payload)
    except ValueError as e:
        raise_from_value_error(e)


@router.put("/airlines/{airline_id}", response_model=AirlineRead)
def update_airline(
    airline_id: int,
    payload: AirlineCreate,
    db: Session = Depends(get_db),
    current_user: Person = Depends(require_admin),
):
    """Обновить данные авиакомпании."""
    service = FlightService(db)
    try:
        return service.update_airline(airline_id, payload)
    except ValueError as e:
        raise_from_value_error(e)


@router.delete("/airlines/{airline_id}", response_model=DeleteResponse)
def delete_airline(
    airline_id: int,
    db: Session = Depends(get_db),
    current_user: Person = Depends(require_admin),
):
    """Удалить авиакомпанию."""
    service = FlightService(db)
    try:
        return service.delete_airline(airline_id)
    except ValueError as e:
        raise_from_value_error(e)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка при удалении: {str(e)}"
        )


# =========================================================
# FLIGHT STATUSES
# =========================================================


@router.get("/statuses/", response_model=List[FlightStatusRead])
def list_flight_statuses(db: Session = Depends(get_db)):
    """Получить список всех статусов рейсов."""
    service = FlightService(db)
    return service.get_all_flight_statuses()


@router.get("/statuses/{status_id}", response_model=FlightStatusRead)
def get_flight_status(status_id: int, db: Session = Depends(get_db)):
    """Получить статус по ID."""
    service = FlightService(db)
    status_flight = service.get_flight_status(status_id)
    if not status_flight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Статус не найден"
        )
    return status_flight


@router.post(
    "/statuses/",
    response_model=FlightStatusRead,
    status_code=status.HTTP_201_CREATED,
)
def create_flight_status(
    payload: FlightStatusCreate,
    db: Session = Depends(get_db),
    current_user: Person = Depends(require_admin),
):
    """Создать новый статус."""
    service = FlightService(db)
    try:
        return service.create_flight_status(payload)
    except ValueError as e:
        raise_from_value_error(e)


@router.delete("/statuses/{status_id}", response_model=DeleteResponse)
def delete_flight_status(
    status_id: int,
    db: Session = Depends(get_db),
    current_user: Person = Depends(require_admin),
):
    """Удалить статус."""
    service = FlightService(db)
    try:
        return service.delete_flight_status(status_id)
    except ValueError as e:
        raise_from_value_error(e)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка при удалении: {str(e)}"
        )


# =========================================================
# FLIGHTS
# =========================================================


@router.get("/", response_model=List[FlightRead])
def list_flights(
    skip: int = Query(0, ge=0, description="Пропустить N записей"),
    limit: int = Query(100, ge=1, le=1000, description="Максимум записей"),
    db: Session = Depends(get_db),
):
    """Получить все рейсы с пагинацией."""
    service = FlightService(db)
    return service.get_all_flights(skip=skip, limit=limit)


@router.get("/upcoming/", response_model=List[FlightRead])
def list_upcoming_flights(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Получить ближайшие рейсы (из будущего)."""
    service = FlightService(db)
    return service.get_upcoming_flights(skip=skip, limit=limit)


@router.get("/{flight_id}", response_model=FlightRead)
def get_flight(flight_id: int, db: Session = Depends(get_db)):
    """Получить рейс по ID."""
    service = FlightService(db)
    flight = service.get_flight(flight_id)
    if not flight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Рейс не найден"
        )
    return flight


@router.post(
    "/",
    response_model=FlightRead,
    status_code=status.HTTP_201_CREATED,
)
def create_flight(
    payload: FlightCreate,
    db: Session = Depends(get_db),
    current_user: Person = Depends(require_admin),
):
    """Создать новый рейс."""
    service = FlightService(db)
    try:
        return service.create_flight(payload)
    except ValueError as e:
        raise_from_value_error(e)


@router.put("/{flight_id}", response_model=FlightRead)
def update_flight(
    flight_id: int,
    payload: FlightUpdate,
    db: Session = Depends(get_db),
    current_user: Person = Depends(require_admin),
):
    """Обновить данные рейса."""
    service = FlightService(db)
    try:
        return service.update_flight(flight_id, payload)
    except ValueError as e:
        raise_from_value_error(e)


@router.delete("/{flight_id}", response_model=DeleteResponse)
def delete_flight(
    flight_id: int,
    db: Session = Depends(get_db),
    current_user: Person = Depends(require_admin),
):
    """Удалить рейс."""
    service = FlightService(db)
    try:
        return service.delete_flight(flight_id)
    except ValueError as e:
        raise_from_value_error(e)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка при удалении: {str(e)}"
        )


# =========================================================
# FLIGHT SEARCH
# =========================================================


@router.post(
    "/search/",
    response_model=List[FlightRead],
    summary="Поиск рейсов",
)
def search_flights(
    criteria: FlightSearch,
    db: Session = Depends(get_db),
):
    """
    Поиск рейсов по критериям.

    Можно искать по:
    - аэропорту вылета
    - аэропорту прилёта
    - диапазону дат
    - авиакомпании
    """
    service = FlightService(db)
    return service.search_flights(criteria)


@router.get(
    "/from-airport/{airport_id}",
    response_model=List[FlightRead],
)
def get_departing_flights(
    airport_id: int,
    db: Session = Depends(get_db),
):
    """Получить все вылетающие рейсы из аэропорта."""
    service = FlightService(db)
    return service.get_flights_by_airport(airport_id, is_departure=True)


@router.get(
    "/to-airport/{airport_id}",
    response_model=List[FlightRead],
)
def get_arriving_flights(
    airport_id: int,
    db: Session = Depends(get_db),
):
    """Получить все прибывающие рейсы в аэропорт."""
    service = FlightService(db)
    return service.get_flights_by_airport(airport_id, is_departure=False)


# =========================================================
# FLIGHT PRICES
# =========================================================


@router.get(
    "/{flight_id}/prices/",
    response_model=List[FlightPriceRead],
)
def get_flight_prices(
    flight_id: int,
    db: Session = Depends(get_db),
):
    """Получить все цены на рейс."""
    service = FlightService(db)
    return service.get_flight_prices_by_flight(flight_id)


@router.post(
    "/prices/",
    response_model=FlightPriceRead,
    status_code=status.HTTP_201_CREATED,
)
def create_flight_price(
    payload: FlightPriceCreate,
    db: Session = Depends(get_db),
    current_user: Person = Depends(require_admin),
):
    """Создать цену на рейс."""
    service = FlightService(db)
    try:
        return service.create_flight_price(payload)
    except ValueError as e:
        raise_from_value_error(e)


@router.put(
    "/prices/{price_id}",
    response_model=FlightPriceRead,
)
def update_flight_price(
    price_id: int,
    new_price: float = Query(..., ge=0, description="Новая цена"),
    db: Session = Depends(get_db),
    current_user: Person = Depends(require_admin),
):
    """Обновить цену на рейс."""
    service = FlightService(db)
    try:
        return service.update_flight_price(price_id, new_price)
    except ValueError as e:
        raise_from_value_error(e)


@router.delete(
    "/prices/{price_id}",
    response_model=DeleteResponse,
)
def delete_flight_price(
    price_id: int,
    db: Session = Depends(get_db),
    current_user: Person = Depends(require_admin),
):
    """Удалить цену на рейс."""
    service = FlightService(db)
    try:
        return service.delete_flight_price(price_id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка при удалении: {str(e)}"
        )
