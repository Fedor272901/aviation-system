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
from app import crud
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
    return crud.flight.get_all_airports(db)


@router.get("/airports/{airport_id}", response_model=AirportRead)
def get_airport(airport_id: int, db: Session = Depends(get_db)):
    """Получить аэропорт по ID."""
    airport = crud.flight.get_airport(db, airport_id)
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
def create_airport(payload: AirportCreate, db: Session = Depends(get_db)):
    """Создать новый аэропорт."""
    try:
        return crud.flight.create_airport(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/airports/{airport_id}", response_model=AirportRead)
def update_airport(airport_id: int, payload: AirportCreate, db: Session = Depends(get_db)):
    """Обновить данные аэропорта."""
    airport = crud.flight.get_airport(db, airport_id)
    if not airport:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Аэропорт не найден"
        )

    try:
        return crud.flight.update_airport(db, airport, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/airports/{airport_id}", response_model=DeleteResponse)
def delete_airport(airport_id: int, db: Session = Depends(get_db)):
    """Удалить аэропорт."""
    airport = crud.flight.get_airport(db, airport_id)
    if not airport:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Аэропорт не найден"
        )

    try:
        return crud.flight.delete_airport(db, airport)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
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
    return crud.flight.get_all_airlines(db)


@router.get("/airlines/{airline_id}", response_model=AirlineRead)
def get_airline(airline_id: int, db: Session = Depends(get_db)):
    """Получить авиакомпанию по ID."""
    airline = crud.flight.get_airline(db, airline_id)
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
def create_airline(payload: AirlineCreate, db: Session = Depends(get_db)):
    """Создать новую авиакомпанию."""
    try:
        return crud.flight.create_airline(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/airlines/{airline_id}", response_model=AirlineRead)
def update_airline(airline_id: int, payload: AirlineCreate, db: Session = Depends(get_db)):
    """Обновить данные авиакомпании."""
    airline = crud.flight.get_airline(db, airline_id)
    if not airline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Авиакомпания не найдена"
        )

    try:
        return crud.flight.update_airline(db, airline, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/airlines/{airline_id}", response_model=DeleteResponse)
def delete_airline(airline_id: int, db: Session = Depends(get_db)):
    """Удалить авиакомпанию."""
    airline = crud.flight.get_airline(db, airline_id)
    if not airline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Авиакомпания не найдена"
        )

    try:
        return crud.flight.delete_airline(db, airline)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
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
    return crud.flight.get_all_flight_statuses(db)


@router.get("/statuses/{status_id}", response_model=FlightStatusRead)
def get_flight_status(status_id: int, db: Session = Depends(get_db)):
    """Получить статус по ID."""
    status = crud.flight.get_flight_status(db, status_id)
    if not status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Статус не найден"
        )
    return status


@router.post(
    "/statuses/",
    response_model=FlightStatusRead,
    status_code=status.HTTP_201_CREATED,
)
def create_flight_status(payload: FlightStatusCreate, db: Session = Depends(get_db)):
    """Создать новый статус."""
    try:
        return crud.flight.create_flight_status(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/statuses/{status_id}", response_model=DeleteResponse)
def delete_flight_status(status_id: int, db: Session = Depends(get_db)):
    """Удалить статус."""
    status = crud.flight.get_flight_status(db, status_id)
    if not status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Статус не найден"
        )

    try:
        return crud.flight.delete_flight_status(db, status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
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
    return crud.flight.get_all_flights(db, skip=skip, limit=limit)


@router.get("/upcoming/", response_model=List[FlightRead])
def list_upcoming_flights(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Получить ближайшие рейсы (из будущего)."""
    return crud.flight.get_upcoming_flights(db, skip=skip, limit=limit)


@router.get("/{flight_id}", response_model=FlightRead)
def get_flight(flight_id: int, db: Session = Depends(get_db)):
    """Получить рейс по ID."""
    flight = crud.flight.get_flight(db, flight_id)
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
def create_flight(payload: FlightCreate, db: Session = Depends(get_db)):
    """Создать новый рейс."""
    try:
        return crud.flight.create_flight(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{flight_id}", response_model=FlightRead)
def update_flight(
    flight_id: int,
    payload: FlightUpdate,
    db: Session = Depends(get_db),
):
    """Обновить данные рейса."""
    flight = crud.flight.get_flight(db, flight_id)
    if not flight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Рейс не найден"
        )

    try:
        return crud.flight.update_flight(db, flight, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{flight_id}", response_model=DeleteResponse)
def delete_flight(flight_id: int, db: Session = Depends(get_db)):
    """Удалить рейс."""
    flight = crud.flight.get_flight(db, flight_id)
    if not flight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Рейс не найден"
        )

    try:
        return crud.flight.delete_flight(db, flight)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
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
    return crud.flight.search_flights(db, criteria)


@router.get(
    "/from-airport/{airport_id}",
    response_model=List[FlightRead],
)
def get_departing_flights(
    airport_id: int,
    db: Session = Depends(get_db),
):
    """Получить все вылетающие рейсы из аэропорта."""
    return crud.flight.get_flights_by_airport(db, airport_id, is_departure=True)


@router.get(
    "/to-airport/{airport_id}",
    response_model=List[FlightRead],
)
def get_arriving_flights(
    airport_id: int,
    db: Session = Depends(get_db),
):
    """Получить все прибывающие рейсы в аэропорт."""
    return crud.flight.get_flights_by_airport(db, airport_id, is_departure=False)


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
    flight = crud.flight.get_flight(db, flight_id)
    if not flight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Рейс не найден"
        )
    return crud.flight.get_flight_prices_by_flight(db, flight_id)


@router.post(
    "/prices/",
    response_model=FlightPriceRead,
    status_code=status.HTTP_201_CREATED,
)
def create_flight_price(payload: FlightPriceCreate, db: Session = Depends(get_db)):
    """Создать цену на рейс."""
    try:
        return crud.flight.create_flight_price(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/prices/{price_id}",
    response_model=FlightPriceRead,
)
def update_flight_price(
    price_id: int,
    new_price: float = Query(..., ge=0, description="Новая цена"),
    db: Session = Depends(get_db),
):
    """Обновить цену на рейс."""
    price = crud.flight.get_flight_price(db, price_id)
    if not price:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Цена не найдена"
        )

    try:
        return crud.flight.update_flight_price(db, price, new_price)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/prices/{price_id}",
    response_model=DeleteResponse,
)
def delete_flight_price(price_id: int, db: Session = Depends(get_db)):
    """Удалить цену на рейс."""
    price = crud.flight.get_flight_price(db, price_id)
    if not price:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Цена не найдена"
        )

    try:
        return crud.flight.delete_flight_price(db, price)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка при удалении: {str(e)}"
        )