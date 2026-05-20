"""Схемы Pydantic для сущностей Ticket (билеты).

Используются для валидации входных/выходных данных API.
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


# =========================================================
# TICKET STATUS
# =========================================================


class TicketStatusBase(BaseModel):
    """Базовая схема для статуса билета."""

    status_name: str = Field(..., max_length=20, description="Название статуса")


class TicketStatusCreate(TicketStatusBase):
    """Создание нового статуса."""

    pass


class TicketStatusRead(TicketStatusBase):
    """Чтение статуса."""

    id: int

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# TICKET
# =========================================================


class TicketBase(BaseModel):
    """Базовая схема для билета."""

    seat_number: str = Field(..., max_length=5, description="Номер места (например, 12A)")
    id_seat_class: int = Field(..., description="ID класса мест")
    price: Decimal = Field(..., ge=0, description="Цена билета")
    id_status: int = Field(..., description="ID статуса билета")
    id_flight: int = Field(..., description="ID рейса")
    id_passenger: int = Field(..., description="ID пассажира (Person)")


class TicketCreate(TicketBase):
    """Создание нового билета."""

    pass


class TicketUpdate(BaseModel):
    """Обновление билета."""

    seat_number: Optional[str] = Field(None, max_length=5)
    id_seat_class: Optional[int] = None
    price: Optional[Decimal] = Field(None, ge=0)
    id_status: Optional[int] = None
    id_flight: Optional[int] = None


class TicketRead(TicketBase):
    """Чтение билета."""

    id: int
    purchase_date: datetime

    # Вложенные данные для удобства (опционально)
    status_name: Optional[str] = Field(None, description="Название статуса")
    flight_number: Optional[str] = Field(None, description="Номер рейса")
    passenger_email: Optional[str] = Field(None, description="Email пассажира")

    model_config = ConfigDict(from_attributes=True)


class TicketSearch(BaseModel):
    """Поиск билетов."""

    id_passenger: Optional[int] = Field(None, description="ID пассажира")
    id_flight: Optional[int] = Field(None, description="ID рейса")
    id_status: Optional[int] = Field(None, description="ID статуса")
    date_from: Optional[datetime] = Field(None, description="Дата с")
    date_to: Optional[datetime] = Field(None, description="Дата по")


class DeleteResponse(BaseModel):
    """Ответ при успешном удалении."""

    message: str
    deleted_id: int