"""Сервисный слой для сущностей Crew (экипаж)."""

from sqlalchemy.orm import Session
from app.crud import crew as crew_crud
from app.models import Crew, FlightRole, CrewAssignment
from app.schemas.crew import CrewCreate, CrewAssignmentCreate, FlightRoleCreate
import logging

logger = logging.getLogger(__name__)


class CrewService:
    """Сервис для работы с экипажем."""

    def __init__(self, db: Session):
        self.db = db

    # =========================================================
    # FLIGHT ROLE
    # =========================================================

    def create_flight_role(self, payload: FlightRoleCreate) -> FlightRole:
        """Создать должность с проверкой уникальности."""
        if crew_crud.get_flight_role_by_name(self.db, payload.role_name):
            raise ValueError(f"Должность '{payload.role_name}' уже существует")
        return crew_crud.create_flight_role(self.db, payload)

    def get_flight_role(self, role_id: int) -> FlightRole | None:
        """Получить должность по ID."""
        return crew_crud.get_flight_role(self.db, role_id)

    def get_all_flight_roles(self) -> list[FlightRole]:
        """Получить все должности."""
        return crew_crud.get_all_flight_roles(self.db)

    def delete_flight_role(self, role_id: int) -> dict:
        """Удалить должность."""
        role = crew_crud.get_flight_role(self.db, role_id)
        if not role:
            raise ValueError("Должность не найдена")
        return crew_crud.delete_flight_role(self.db, role)

    # =========================================================
    # CREW
    # =========================================================

    def create_crew(self, payload: CrewCreate) -> Crew:
        """Создать сотрудника с проверкой дубликатов."""
        from app.crud import person as person_crud

        person = person_crud.get_person(self.db, payload.person_id)
        if not person:
            raise ValueError("Пользователь не найден")

        existing = crew_crud.get_crew_by_person(self.db, payload.person_id)
        if existing:
            raise ValueError("Этот пользователь уже является сотрудником экипажа")

        return crew_crud.create_crew(self.db, payload)

    def get_crew(self, crew_id: int) -> Crew | None:
        """Получить сотрудника по ID."""
        return crew_crud.get_crew(self.db, crew_id)

    def get_all_crew(self, skip: int = 0, limit: int = 100) -> list[Crew]:
        """Получить всех сотрудников с пагинацией."""
        return crew_crud.get_all_crew(self.db, skip, limit)

    def update_crew(self, crew_id: int, person_id: int) -> Crew:
        """Обновить данные сотрудника."""
        crew = crew_crud.get_crew(self.db, crew_id)
        if not crew:
            raise ValueError("Сотрудник не найден")

        from app.crud import person as person_crud

        person = person_crud.get_person(self.db, person_id)
        if not person:
            raise ValueError("Пользователь не найден")

        existing = crew_crud.get_crew_by_person(self.db, person_id)
        if existing and existing.id != crew.id:
            raise ValueError("Этот пользователь уже назначен в экипаж")

        return crew_crud.update_crew(self.db, crew, person_id)

    def delete_crew(self, crew_id: int) -> dict:
        """Удалить сотрудника из экипажа."""
        crew = crew_crud.get_crew(self.db, crew_id)
        if not crew:
            raise ValueError("Сотрудник не найден")
        return crew_crud.delete_crew(self.db, crew)

    # =========================================================
    # CREW ASSIGNMENT
    # =========================================================

    def create_crew_assignment(self, payload: CrewAssignmentCreate) -> CrewAssignment:
        """Назначить сотрудника на рейс с проверками."""
        from sqlalchemy import select

        crew = crew_crud.get_crew(self.db, payload.id_crew)
        if not crew:
            raise ValueError("Сотрудник экипажа не найден")

        from app.models import Flight

        flight = self.db.get(Flight, payload.id_flight)
        if not flight:
            raise ValueError("Рейс не найден")

        flight_role = crew_crud.get_flight_role(self.db, payload.id_flight_role)
        if not flight_role:
            raise ValueError("Должность не найдена")

        existing = self.db.scalar(
            select(CrewAssignment).where(
                CrewAssignment.id_flight == payload.id_flight,
                CrewAssignment.id_crew == payload.id_crew,
                CrewAssignment.id_flight_role == payload.id_flight_role,
            )
        )
        if existing:
            raise ValueError(
                "Этот сотрудник уже назначен на этот рейс с этой должностью"
            )

        return crew_crud.create_crew_assignment(self.db, payload)

    def get_crew_assignment(self, assignment_id: int) -> CrewAssignment | None:
        """Получить назначение по ID."""
        return crew_crud.get_crew_assignment(self.db, assignment_id)

    def get_all_crew_assignments(
        self, skip: int = 0, limit: int = 100
    ) -> list[CrewAssignment]:
        """Получить все назначения с пагинацией."""
        return crew_crud.get_all_crew_assignments(self.db, skip, limit)

    def get_assignments_by_flight(self, flight_id: int) -> list[CrewAssignment]:
        """Получить всех сотрудников на рейс."""
        return crew_crud.get_assignments_by_flight(self.db, flight_id)

    def get_assignments_by_crew(self, crew_id: int) -> list[CrewAssignment]:
        """Получить все назначения сотрудника."""
        return crew_crud.get_assignments_by_crew(self.db, crew_id)

    def delete_crew_assignment(self, assignment_id: int) -> dict:
        """Удалить назначение."""
        assignment = crew_crud.get_crew_assignment(self.db, assignment_id)
        if not assignment:
            raise ValueError("Назначение не найдено")
        return crew_crud.delete_crew_assignment(self.db, assignment)
