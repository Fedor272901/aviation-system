"""HTTP эндпоинты для управления самолётами (Aircraft).

Включает:
- CRUD для SeatClass (классы мест)
- CRUD для ModelAircraft (модели самолётов)
- CRUD для ModelSeat (распределение мест)
- CRUD для Aircraft (самолёты)
- CRUD для AircraftLease (аренда)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from app.dependencies import get_db
from app.utils.api_utils import raise_from_value_error
from app.services.aircraft import AircraftService
from app.schemas.aircraft import (
    SeatClassCreate,
    SeatClassRead,
    ModelAircraftCreate,
    ModelAircraftRead,
    ModelSeatCreate,
    ModelSeatRead,
    AircraftCreate,
    AircraftUpdate,
    AircraftRead,
    AircraftLeaseCreate,
    AircraftLeaseRead,
    DeleteResponse,
)

router = APIRouter(prefix="/aircraft", tags=["Aircraft"])


# =========================================================
# SEAT CLASSES
# =========================================================


@router.get("/seat-classes/", response_model=List[SeatClassRead])
def list_seat_classes(db: Session = Depends(get_db)):
    """Получить все классы мест."""
    service = AircraftService(db)
    return service.get_all_seat_classes()


@router.get("/seat-classes/{class_id}", response_model=SeatClassRead)
def get_seat_class(class_id: int, db: Session = Depends(get_db)):
    """Получить класс мест по ID."""
    service = AircraftService(db)
    seat_class = service.get_seat_class(class_id)
    if not seat_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Класс мест не найден"
        )
    return seat_class


@router.post(
    "/seat-classes/",
    response_model=SeatClassRead,
    status_code=status.HTTP_201_CREATED,
)
def create_seat_class(payload: SeatClassCreate, db: Session = Depends(get_db)):
    """Создать новый класс мест."""
    service = AircraftService(db)
    try:
        return service.create_seat_class(payload)
    except ValueError as e:
        raise_from_value_error(e)


@router.put("/seat-classes/{class_id}", response_model=SeatClassRead)
def update_seat_class(
    class_id: int, payload: SeatClassCreate, db: Session = Depends(get_db)
):
    """Обновить данные класса мест."""
    service = AircraftService(db)
    try:
        return service.update_seat_class(class_id, payload)
    except ValueError as e:
        raise_from_value_error(e)


@router.delete("/seat-classes/{class_id}", response_model=DeleteResponse)
def delete_seat_class(class_id: int, db: Session = Depends(get_db)):
    """Удалить класс мест."""
    service = AircraftService(db)
    try:
        return service.delete_seat_class(class_id)
    except ValueError as e:
        raise_from_value_error(e)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка при удалении: {str(e)}"
        )


# =========================================================
# MODEL AIRCRAFT
# =========================================================


@router.get("/models/", response_model=List[ModelAircraftRead])
def list_model_aircraft(db: Session = Depends(get_db)):
    """Получить все модели самолётов."""
    service = AircraftService(db)
    return service.get_all_model_aircraft()


@router.get("/models/{model_id}", response_model=ModelAircraftRead)
def get_model_aircraft(model_id: int, db: Session = Depends(get_db)):
    """Получить модель самолёта по ID."""
    service = AircraftService(db)
    model = service.get_model_aircraft(model_id)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Модель не найдена"
        )
    return model


@router.post(
    "/models/",
    response_model=ModelAircraftRead,
    status_code=status.HTTP_201_CREATED,
)
def create_model_aircraft(
    payload: ModelAircraftCreate, db: Session = Depends(get_db)
):
    """Создать новую модель самолёта с распределением мест."""
    service = AircraftService(db)
    try:
        return service.create_model_aircraft(payload)
    except ValueError as e:
        raise_from_value_error(e)


@router.put("/models/{model_id}", response_model=ModelAircraftRead)
def update_model_aircraft(
    model_id: int, payload: ModelAircraftCreate, db: Session = Depends(get_db)
):
    """Обновить данные модели самолёта."""
    service = AircraftService(db)
    try:
        return service.update_model_aircraft(model_id, payload)
    except ValueError as e:
        raise_from_value_error(e)


@router.delete("/models/{model_id}", response_model=DeleteResponse)
def delete_model_aircraft(model_id: int, db: Session = Depends(get_db)):
    """Удалить модель самолёта."""
    service = AircraftService(db)
    try:
        return service.delete_model_aircraft(model_id)
    except ValueError as e:
        raise_from_value_error(e)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка при удалении: {str(e)}"
        )


# =========================================================
# MODEL SEATS
# =========================================================


@router.get("/model-seats/model/{model_id}", response_model=List[ModelSeatRead])
def get_model_seats_by_model(model_id: int, db: Session = Depends(get_db)):
    """Получить все распределения мест для модели."""
    service = AircraftService(db)
    return service.get_model_seats_by_model(model_id)


@router.post(
    "/model-seats/",
    response_model=ModelSeatRead,
    status_code=status.HTTP_201_CREATED,
)
def create_model_seat(payload: ModelSeatCreate, db: Session = Depends(get_db)):
    """Создать распределение мест."""
    service = AircraftService(db)
    try:
        return service.create_model_seat(payload)
    except ValueError as e:
        raise_from_value_error(e)


@router.put("/model-seats/{seat_id}", response_model=ModelSeatRead)
def update_model_seat(
    seat_id: int,
    seat_count: int = Query(..., gt=0, description="Количество мест"),
    db: Session = Depends(get_db),
):
    """Обновить количество мест."""
    service = AircraftService(db)
    try:
        return service.update_model_seat(seat_id, seat_count)
    except ValueError as e:
        raise_from_value_error(e)


@router.delete("/model-seats/{seat_id}", response_model=DeleteResponse)
def delete_model_seat(seat_id: int, db: Session = Depends(get_db)):
    """Удалить распределение мест."""
    service = AircraftService(db)
    try:
        return service.delete_model_seat(seat_id)
    except ValueError as e:
        raise_from_value_error(e)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка при удалении: {str(e)}"
        )


# =========================================================
# AIRCRAFT
# =========================================================


@router.get("/", response_model=List[AircraftRead])
def list_aircraft(
    skip: int = Query(0, ge=0, description="Пропустить N записей"),
    limit: int = Query(100, ge=1, le=1000, description="Максимум записей"),
    db: Session = Depends(get_db),
):
    """Получить все самолёты с пагинацией."""
    service = AircraftService(db)
    return service.get_all_aircraft(skip=skip, limit=limit)


@router.get("/{aircraft_id}", response_model=AircraftRead)
def get_aircraft(aircraft_id: int, db: Session = Depends(get_db)):
    """Получить самолёт по ID."""
    service = AircraftService(db)
    aircraft = service.get_aircraft(aircraft_id)
    if not aircraft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Самолёт не найден"
        )
    return aircraft


@router.post(
    "/",
    response_model=AircraftRead,
    status_code=status.HTTP_201_CREATED,
)
def create_aircraft(payload: AircraftCreate, db: Session = Depends(get_db)):
    """Создать новый самолёт."""
    service = AircraftService(db)
    try:
        return service.create_aircraft(payload)
    except ValueError as e:
        raise_from_value_error(e)


@router.put("/{aircraft_id}", response_model=AircraftRead)
def update_aircraft(
    aircraft_id: int, payload: AircraftUpdate, db: Session = Depends(get_db)
):
    """Обновить данные самолёта."""
    service = AircraftService(db)
    try:
        return service.update_aircraft(aircraft_id, payload)
    except ValueError as e:
        raise_from_value_error(e)


@router.delete("/{aircraft_id}", response_model=DeleteResponse)
def delete_aircraft(aircraft_id: int, db: Session = Depends(get_db)):
    """Удалить самолёт."""
    service = AircraftService(db)
    try:
        return service.delete_aircraft(aircraft_id)
    except ValueError as e:
        raise_from_value_error(e)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка при удалении: {str(e)}"
        )


# =========================================================
# AIRCRAFT LEASES
# =========================================================


@router.get("/leases/", response_model=List[AircraftLeaseRead])
def list_aircraft_leases(db: Session = Depends(get_db)):
    """Получить все аренды самолётов."""
    service = AircraftService(db)
    return service.get_all_aircraft_leases()


@router.get("/leases/{lease_id}", response_model=AircraftLeaseRead)
def get_aircraft_lease(lease_id: int, db: Session = Depends(get_db)):
    """Получить аренду по ID."""
    service = AircraftService(db)
    lease = service.get_aircraft_lease(lease_id)
    if not lease:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Аренда не найдена"
        )
    return lease


@router.post(
    "/leases/",
    response_model=AircraftLeaseRead,
    status_code=status.HTTP_201_CREATED,
)
def create_aircraft_lease(payload: AircraftLeaseCreate, db: Session = Depends(get_db)):
    """Создать аренду самолёта."""
    service = AircraftService(db)
    try:
        return service.create_aircraft_lease(payload)
    except ValueError as e:
        raise_from_value_error(e)


@router.put("/leases/{lease_id}", response_model=AircraftLeaseRead)
def update_aircraft_lease(
    lease_id: int,
    end_date: date = Query(..., description="Дата окончания аренды (NULL = бессрочно)"),
    db: Session = Depends(get_db),
):
    """Обновить дату окончания аренды."""
    service = AircraftService(db)
    try:
        return service.update_aircraft_lease(lease_id, end_date)
    except ValueError as e:
        raise_from_value_error(e)


@router.delete("/leases/{lease_id}", response_model=DeleteResponse)
def delete_aircraft_lease(lease_id: int, db: Session = Depends(get_db)):
    """Удалить аренду самолёта."""
    service = AircraftService(db)
    try:
        return service.delete_aircraft_lease(lease_id)
    except ValueError as e:
        raise_from_value_error(e)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка при удалении: {str(e)}"
        )
