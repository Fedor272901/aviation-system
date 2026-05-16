"""Initial schema

Revision ID: b2f5a545ed35
Revises:
Create Date: 2026-05-16 23:30:09.145758

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# Импортируем Base со всеми моделями
from app.models.base import Base
from app.models import (
    Person, SystemRole, PeopleSystemRole,
    Crew, FlightRole, CrewAssignment,
    Airport, Airline, FlightStatus, Flight, FlightPrice,
    SeatClass, ModelAircraft, ModelSeat, Aircraft, AircraftLease,
    TicketStatus, Ticket,
)


revision: str = 'b2f5a545ed35'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables from models."""
    Base.metadata.create_all(op.get_bind())


def downgrade() -> None:
    """Drop all tables."""
    Base.metadata.drop_all(op.get_bind())