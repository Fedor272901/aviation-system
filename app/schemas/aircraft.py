"""Схемы Pydantic для сущностей Aircraft (самолёты).

Используются для валидации входных/выходных данных API.
"""

from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional
from datetime import date
from decimal import Decimal


# =========================================================
# SEAT CLASS
# =========================================================


class SeatClassBase(BaseModel):
    """Базовая схема для класса мест."""

    class_name: str = Field(..., max_length=20, description="Название класса")
    price_multiplier: Decimal = Field(
        ..., ge=0, le=10, description="Множитель цены (1.0 = базовая)"
    )
    description: Optional[str] = Field(None, max_length=100, description="Описание")

    @field_validator("class_name")
    @classmethod
    def validate_class_name(cls, v: str) -> str:
        """Проверка названия класса."""
        allowed = ["Эконом", "Бизнес", "Первый", "Premium"]
        if v not in allowed:
            raise ValueError(f"Недопустимый класс: {v}. Доступные: {allowed}")
        return v


class SeatClassCreate(SeatClassBase):
    """Создание нового класса мест."""

    pass


class SeatClassRead(SeatClassBase):
    """Чтение класса мест."""

    id: int

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# MODEL AIRCRAFT
# =========================================================


class ModelAircraftBase(BaseModel):
    """Базовая схема для модели самолёта."""

    name: str = Field(..., max_length=30, description="Модель (например, Boeing 737)")
    manufacturer: Optional[str] = Field(
        None, max_length=30, description="Производитель"
    )


class ModelAircraftCreate(ModelAircraftBase):
    """Создание новой модели самолёта."""

    seats: list[dict] = Field(
        ...,
        description="Список распределения мест: [{'class_id': 1, 'count': 150}, ...]",
    )


class ModelAircraftRead(ModelAircraftBase):
    """Чтение модели самолёта."""

    id: int

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# MODEL SEATS
# =========================================================


class ModelSeatBase(BaseModel):
    """Базовая схема для распределения мест."""

    id_model: int = Field(..., description="ID модели самолёта")
    id_seat_class: int = Field(..., description="ID класса мест")
    seat_count: int = Field(..., gt=0, description="Количество мест")


class ModelSeatCreate(ModelSeatBase):
    """Создание распределения мест."""

    pass


class ModelSeatRead(ModelSeatBase):
    """Чтение распределения мест."""

    id: int

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# AIRCRAFT
# =========================================================


class AircraftBase(BaseModel):
    """Базовая схема для самолёта."""

    registration_number: str = Field(
        ..., max_length=10, description="Регистрационный номер (бортовой)"
    )
    id_model: int = Field(..., description="ID модели самолёта")
    manufacture_year: Optional[int] = Field(
        None, ge=1900, le=2100, description="Год выпуска"
    )
    last_maintenance: Optional[date] = Field(
        None, description="Последнее техобслуживание"
    )


class AircraftCreate(AircraftBase):
    """Создание нового самолёта."""

    pass


class AircraftUpdate(BaseModel):
    """Обновление самолёта."""

    registration_number: Optional[str] = Field(None, max_length=10)
    id_model: Optional[int] = None
    manufacture_year: Optional[int] = Field(None, ge=1900, le=2100)
    last_maintenance: Optional[date] = None


class AircraftRead(AircraftBase):
    """Чтение самолёта."""

    id: int

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# AIRCRAFT LEASE
# =========================================================


class AircraftLeaseBase(BaseModel):
    """Базовая схема для аренды самолёта."""

    id_aircraft: int = Field(..., description="ID самолёта")
    id_airline: int = Field(..., description="ID авиакомпании")
    start_date: date = Field(..., description="Дата начала аренды")
    end_date: Optional[date] = Field(None, description="Дата окончания аренды (NULL = бессрочно)")


class AircraftLeaseCreate(AircraftLeaseBase):
    """Создание аренды самолёта."""

    pass


class AircraftLeaseRead(AircraftLeaseBase):
    """Чтение аренды самолёта."""

    id: int

    model_config = ConfigDict(from_attributes=True)


class DeleteResponse(BaseModel):
    """Ответ при успешном удалении."""

    message: str
    deleted_id: int