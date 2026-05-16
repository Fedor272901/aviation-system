from logging.config import fileConfig
import os

from sqlalchemy import engine_from_config, pool
from dotenv import load_dotenv

from alembic import context

# Импортируем Base И все модели, чтобы metadata заполнилась
from app.models.base import Base
from app.models import (
    Person, SystemRole, PeopleSystemRole,
    Crew, FlightRole, CrewAssignment,
    Airport, Airline, FlightStatus, Flight, FlightPrice,
    SeatClass, ModelAircraft, ModelSeat, Aircraft, AircraftLease,
    TicketStatus, Ticket,
)


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL не найден в окружении")

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def include_object(object, name, type_, reflected, compare_to):
    """
    Исключаем системные таблицы MSSQL из миграций.
    """
    if type_ == "table" and name == "sysdiagrams":
        return False
    return True


def run_migrations_offline() -> None:
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        url=DATABASE_URL,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()