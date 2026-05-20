"""CRUD операции для сущностей Crew (экипаж).

Отвечает только за работу с базой данных (SELECT, INSERT, UPDATE, DELETE).
Бизнес-логика находится в services/.
"""

from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import Crew, FlightRole, CrewAssignment, Person, Flight
from app.schemas.crew import (
    CrewCreate,
    CrewAssignmentCreate,
    FlightRoleCreate,
)
import logging

logger = logging.getLogger(__name__)


# =========================================================
# FLIGHT ROLE
# =========================================================


def get_flight_role(db: Session, role_id: int) -> FlightRole | None:
    """Получить должность по ID."""
    return db.get(FlightRole, role_id)


def get_all_flight_roles(db: Session) -> list[FlightRole]:
    """Получить все должности."""
    return db.execute(select(FlightRole).order_by(FlightRole.id)).scalars().all()


def create_flight_role(db: Session, payload: FlightRoleCreate) -> FlightRole:
    """Создать новую должность (без проверок - только INSERT)."""
    role = FlightRole(role_name=payload.role_name)
    db.add(role)
    db.commit()
    db.refresh(role)

    logger.info(f"Создана должность: {role.role_name} (id={role.id})")
    return role


def get_flight_role_by_name(db: Session, role_name: str) -> FlightRole | None:
    """Получить должность по имени."""
    return db.scalar(
        select(FlightRole).where(FlightRole.role_name == role_name)
    )


def delete_flight_role(db: Session, role: FlightRole) -> dict:
    """Удалить должность (без проверок - только DELETE)."""
    role_id = role.id
    role_name = role.role_name

    logger.info(f"Удалена должность: {role_name} (id={role_id})")

    db.delete(role)
    db.commit()

    return {
        "message": "Должность успешно удалена",
        "deleted_id": role_id,
        "deleted_name": role_name,
    }


# =========================================================
# CREW
# =========================================================


def get_crew(db: Session, crew_id: int) -> Crew | None:
    """Получить сотрудника по ID."""
    return db.get(Crew, crew_id)


def get_crew_by_person(db: Session, person_id: int) -> Crew | None:
    """Получить сотрудника по ID пользователя."""
    return db.scalar(select(Crew).where(Crew.person_id == person_id))


def get_all_crew(db: Session, skip: int = 0, limit: int = 100) -> list[Crew]:
    """Получить всех сотрудников с пагинацией."""
    return (
        db.execute(
            select(Crew).order_by(Crew.id).offset(skip).limit(limit)
        )
        .scalars()
        .all()
    )


def create_crew(db: Session, payload: CrewCreate) -> Crew:
    """Создать нового сотрудника экипажа (без проверок - только INSERT)."""
    crew = Crew(person_id=payload.person_id)
    db.add(crew)
    db.commit()
    db.refresh(crew)

    logger.info(f"Создан сотрудник экипажа: person_id={crew.person_id} (id={crew.id})")
    return crew


def update_crew(db: Session, crew: Crew, person_id: int) -> Crew:
    """Обновить данные сотрудника (без проверок - только UPDATE)."""
    crew.person_id = person_id
    db.commit()
    db.refresh(crew)

    logger.info(f"Обновлен сотрудник экипажа: id={crew.id}, person_id={person_id}")
    return crew


def delete_crew(db: Session, crew: Crew) -> dict:
    """Удалить сотрудника из экипажа (без проверок - только DELETE)."""
    crew_id = crew.id
    person_id = crew.person_id

    logger.info(f"Удален сотрудник экипажа: id={crew_id}, person_id={person_id}")

    db.delete(crew)
    db.commit()

    return {
        "message": "Сотрудник успешно удалён из экипажа",
        "deleted_id": crew_id,
        "person_id": person_id,
    }


# =========================================================
# CREW ASSIGNMENT
# =========================================================


def get_crew_assignment(db: Session, assignment_id: int) -> CrewAssignment | None:
    """Получить назначение по ID."""
    return db.get(CrewAssignment, assignment_id)


def get_all_crew_assignments(
    db: Session, skip: int = 0, limit: int = 100
) -> list[CrewAssignment]:
    """Получить все назначения с пагинацией."""
    return (
        db.execute(
            select(CrewAssignment).order_by(CrewAssignment.id).offset(skip).limit(limit)
        )
        .scalars()
        .all()
    )


def get_assignments_by_flight(
    db: Session, flight_id: int
) -> list[CrewAssignment]:
    """Получить всех назначенных сотрудников на рейс."""
    return (
        db.execute(
            select(CrewAssignment)
            .where(CrewAssignment.id_flight == flight_id)
            .order_by(CrewAssignment.id_flight_role)
        )
        .scalars()
        .all()
    )


def get_assignments_by_crew(
    db: Session, crew_id: int
) -> list[CrewAssignment]:
    """Получить все назначения сотрудника."""
    return (
        db.execute(
            select(CrewAssignment)
            .where(CrewAssignment.id_crew == crew_id)
            .order_by(CrewAssignment.id_flight)
        )
        .scalars()
        .all()
    )


def create_crew_assignment(
    db: Session, payload: CrewAssignmentCreate
) -> CrewAssignment:
    """Создать назначение сотрудника на рейс (без проверок - только INSERT)."""
    assignment = CrewAssignment(
        id_flight_role=payload.id_flight_role,
        id_flight=payload.id_flight,
        id_crew=payload.id_crew,
    )

    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    logger.info(
        f"Создано назначение: crew={assignment.id_crew}, "
        f"flight={assignment.id_flight}, role={assignment.id_flight_role}"
    )
    return assignment


def delete_crew_assignment(db: Session, assignment: CrewAssignment) -> dict:
    """Удалить назначение сотрудника с рейса (без проверок - только DELETE)."""
    assignment_id = assignment.id
    flight_id = assignment.id_flight
    crew_id = assignment.id_crew

    logger.info(
        f"Удалено назначение: id={assignment_id}, "
        f"flight={flight_id}, crew={crew_id}"
    )

    db.delete(assignment)
    db.commit()

    return {
        "message": "Назначение успешно удалено",
        "deleted_id": assignment_id,
        "flight_id": flight_id,
        "crew_id": crew_id,
    }