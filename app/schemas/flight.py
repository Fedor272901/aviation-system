"""Схемы Pydantic для сущностей Flight (рейсы).

Используются для валидации входных/выходных данных API.
"""

from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Optional, Any
from datetime import datetime
from decimal import Decimal


# =========================================================
# AIRPORT
# =========================================================


class AirportBase(BaseModel):
    """Базовая схема для аэропорта."""

    code: str = Field(..., max_length=3, description="Код аэропорта (IATA, 3 символа)")
    name: Optional[str] = Field(None, max_length=30, description="Название аэропорта")
    city: str = Field(..., max_length=30, description="Город")


class AirportCreate(AirportBase):
    """Создание нового аэропорта."""

    pass


class AirportRead(AirportBase):
    """Чтение аэропорта."""

    id: int

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# AIRLINE
# =========================================================


class AirlineBase(BaseModel):
    """Базовая схема для авиакомпании."""

    name: str = Field(..., max_length=30, description="Название авиакомпании")
    code: str = Field(..., max_length=3, description="Код авиакомпании (IATA, 3 символа)")
    country: Optional[str] = Field(None, max_length=30, description="Страна")


class AirlineCreate(AirlineBase):
    """Создание новой авиакомпании."""

    pass


class AirlineRead(AirlineBase):
    """Чтение авиакомпании."""

    id: int

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# FLIGHT STATUS
# =========================================================


class FlightStatusBase(BaseModel):
    """Базовая схема для статуса рейса."""

    status_name: str = Field(..., max_length=20, description="Название статуса")


class FlightStatusCreate(FlightStatusBase):
    """Создание нового статуса."""

    pass


class FlightStatusRead(FlightStatusBase):
    """Чтение статуса."""

    id: int

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# FLIGHT
# =========================================================


class FlightBase(BaseModel):
    """Базовая схема для рейса."""

    flight_number: str = Field(..., max_length=10, description="Номер рейса")
    departure_datetime: datetime = Field(..., description="Время вылета")
    arrival_datetime: datetime = Field(..., description="Время прилёта")
    id_from: int = Field(..., description="ID аэропорта вылета")
    id_to: int = Field(..., description="ID аэропорта прилёта")
    id_airline: int = Field(..., description="ID авиакомпании")
    id_aircraft: int = Field(..., description="ID самолёта")
    id_status: int = Field(..., description="ID статуса рейса")


class FlightCreate(FlightBase):
    """Создание нового рейса."""

    pass


class FlightUpdate(BaseModel):
    """Обновление рейса."""

    flight_number: Optional[str] = Field(None, max_length=10)
    departure_datetime: Optional[datetime] = None
    arrival_datetime: Optional[datetime] = None
    id_from: Optional[int] = None
    id_to: Optional[int] = None
    id_airline: Optional[int] = None
    id_aircraft: Optional[int] = None
    id_status: Optional[int] = None


class FlightRead(FlightBase):
    """Чтение рейса."""

    id: int

    # Вложенные данные для удобства (опционально)
    from_airport_code: Optional[str] = Field(None, description="Код аэропорта вылета")
    to_airport_code: Optional[str] = Field(None, description="Код аэропорта прилёта")
    airline_name: Optional[str] = Field(None, description="Название авиакомпании")
    status_name: Optional[str] = Field(None, description="Статус рейса")

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def extract_related_names(cls, data: Any) -> Any:
        """Извлекает коды аэропортов, имя авиакомпании и статус из relationship."""
        if hasattr(data, "from_airport") and data.from_airport is not None:
            data.from_airport_code = data.from_airport.code
        if hasattr(data, "to_airport") and data.to_airport is not None:
            data.to_airport_code = data.to_airport.code
        if hasattr(data, "airline") and data.airline is not None:
            data.airline_name = data.airline.name
        if hasattr(data, "status") and data.status is not None:
            data.status_name = data.status.status_name
        return data


class FlightSearch(BaseModel):
    """Поиск рейсов."""

    id_from: Optional[int] = Field(None, description="Аэропорт вылета")
    id_to: Optional[int] = Field(None, description="Аэропорт прилёта")
    date_from: Optional[datetime] = Field(None, description="Дата с")
    date_to: Optional[datetime] = Field(None, description="Дата по")
    id_airline: Optional[int] = Field(None, description="Авиакомпания")


# =========================================================
# FLIGHT PRICE
# =========================================================


class FlightPriceBase(BaseModel):
    """Базовая схема для цены рейса."""

    id_flight: int = Field(..., description="ID рейса")
    id_seat_class: int = Field(..., description="ID класса мест")
    price: Decimal = Field(..., ge=0, description="Цена билета")
    valid_from: Optional[datetime] = Field(None, description="Дата начала действия цены")
    valid_to: Optional[datetime] = Field(None, description="Дата окончания действия цены")


class FlightPriceCreate(FlightPriceBase):
    """Создание цены на рейс."""

    pass


class FlightPriceRead(FlightPriceBase):
    """Чтение цены рейса."""

    id: int

    model_config = ConfigDict(from_attributes=True)


class DeleteResponse(BaseModel):
    """Ответ при успешном удалении."""

    message: str
    deleted_id: int
