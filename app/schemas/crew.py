"""Схемы Pydantic для сущностей Crew (экипаж).

Используются для валидации входных/выходных данных API.
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class FlightRoleBase(BaseModel):
    """Базовая схема для роли в полёте."""

    role_name: str = Field(..., max_length=20, description="Название должности")


class FlightRoleCreate(FlightRoleBase):
    """Создание новой должности."""

    pass


class FlightRoleRead(FlightRoleBase):
    """Чтение должности."""

    id: int

    model_config = ConfigDict(from_attributes=True)


class CrewBase(BaseModel):
    """Базовая схема для сотрудника экипажа."""

    person_id: int = Field(..., description="ID связанного пользователя (Person)")


class CrewCreate(CrewBase):
    """Создание нового сотрудника экипажа."""

    pass


class CrewRead(CrewBase):
    """Чтение сотрудника экипажа."""

    id: int
    person_id: int

    model_config = ConfigDict(from_attributes=True)


class CrewAssignmentBase(BaseModel):
    """Базовая схема для назначения на рейс."""

    id_flight_role: int = Field(..., description="ID должности (FlightRole)")
    id_flight: int = Field(..., description="ID рейса (Flight)")
    id_crew: int = Field(..., description="ID сотрудника (Crew)")


class CrewAssignmentCreate(CrewAssignmentBase):
    """Создание назначения сотрудника на рейс."""

    pass


class CrewAssignmentRead(CrewAssignmentBase):
    """Чтение назначения сотрудника на рейс."""

    id: int

    # Вложенные данные для удобства (опционально)
    flight_role_name: Optional[str] = Field(None, description="Название должности")
    flight_number: Optional[str] = Field(None, description="Номер рейса")
    crew_person_email: Optional[str] = Field(None, description="Email сотрудника")

    model_config = ConfigDict(from_attributes=True)


class DeleteResponse(BaseModel):
    """Ответ при успешном удалении."""

    message: str
    deleted_id: int