"""HTTP эндпоинты для управления экипажем (Crew).

Включает:
- CRUD для FlightRole (должности)
- CRUD для Crew (сотрудники)
- CRUD для CrewAssignment (назначения на рейсы)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.dependencies import get_db
from app.dependencies.auth import get_current_user, require_admin
from app.models import Person
from app.services.crew import CrewService
from app.schemas.crew import (
    FlightRoleCreate,
    FlightRoleRead,
    CrewCreate,
    CrewRead,
    CrewAssignmentCreate,
    CrewAssignmentRead,
    DeleteResponse,
)

router = APIRouter(prefix="/crew", tags=["Crew"])


# =========================================================
# FLIGHT ROLES
# =========================================================


@router.get("/roles/", response_model=List[FlightRoleRead])
def list_flight_roles(db: Session = Depends(get_db)):
    """Получить список всех должностей."""
    service = CrewService(db)
    return service.get_all_flight_roles()


@router.get("/roles/{role_id}", response_model=FlightRoleRead)
def get_flight_role(role_id: int, db: Session = Depends(get_db)):
    """Получить должность по ID."""
    service = CrewService(db)
    role = service.get_flight_role(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Должность не найдена"
        )
    return role


@router.post(
    "/roles/",
    response_model=FlightRoleRead,
    status_code=status.HTTP_201_CREATED,
)
def create_flight_role(
    payload: FlightRoleCreate,
    db: Session = Depends(get_db),
    current_user: Person = Depends(require_admin),
):
    """Создать новую должность."""
    service = CrewService(db)
    try:
        return service.create_flight_role(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/roles/{role_id}",
    response_model=DeleteResponse,
)
def delete_flight_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: Person = Depends(require_admin),
):
    """Удалить должность."""
    service = CrewService(db)
    try:
        return service.delete_flight_role(role_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении: {str(e)}")


# =========================================================
# CREW
# =========================================================


@router.get("/", response_model=List[CrewRead])
def list_crew(
    skip: int = Query(0, ge=0, description="Пропустить N записей"),
    limit: int = Query(100, ge=1, le=1000, description="Максимум записей"),
    db: Session = Depends(get_db),
):
    """Получить список всех сотрудников экипажа с пагинацией."""
    service = CrewService(db)
    return service.get_all_crew(skip=skip, limit=limit)


@router.get("/{crew_id}", response_model=CrewRead)
def get_crew(crew_id: int, db: Session = Depends(get_db)):
    """Получить сотрудника по ID."""
    service = CrewService(db)
    crew = service.get_crew(crew_id)
    if not crew:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Сотрудник не найден"
        )
    return crew


@router.post(
    "/",
    response_model=CrewRead,
    status_code=status.HTTP_201_CREATED,
)
def create_crew(
    payload: CrewCreate,
    db: Session = Depends(get_db),
    current_user: Person = Depends(require_admin),
):
    """Создать нового сотрудника экипажа."""
    service = CrewService(db)
    try:
        return service.create_crew(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{crew_id}", response_model=CrewRead)
def update_crew(
    crew_id: int,
    payload: CrewCreate,
    db: Session = Depends(get_db),
    current_user: Person = Depends(require_admin),
):
    """Обновить данные сотрудника."""
    service = CrewService(db)
    try:
        return service.update_crew(crew_id, payload.person_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{crew_id}", response_model=DeleteResponse)
def delete_crew(
    crew_id: int,
    db: Session = Depends(get_db),
    current_user: Person = Depends(require_admin),
):
    """Удалить сотрудника из экипажа."""
    service = CrewService(db)
    try:
        return service.delete_crew(crew_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении: {str(e)}")


# =========================================================
# CREW ASSIGNMENTS
# =========================================================


@router.get(
    "/assignments/",
    response_model=List[CrewAssignmentRead],
)
def list_assignments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Получить все назначения сотрудников на рейсы."""
    service = CrewService(db)
    return service.get_all_crew_assignments(skip=skip, limit=limit)


@router.get(
    "/assignments/flight/{flight_id}",
    response_model=List[CrewAssignmentRead],
)
def get_assignments_by_flight(
    flight_id: int,
    db: Session = Depends(get_db),
):
    """Получить всех сотрудников, назначенных на рейс."""
    service = CrewService(db)
    return service.get_assignments_by_flight(flight_id)


@router.get(
    "/assignments/crew/{crew_id}",
    response_model=List[CrewAssignmentRead],
)
def get_assignments_by_crew(
    crew_id: int,
    db: Session = Depends(get_db),
):
    """Получить все назначения сотрудника."""
    service = CrewService(db)
    return service.get_assignments_by_crew(crew_id)


@router.post(
    "/assignments/",
    response_model=CrewAssignmentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_assignment(
    payload: CrewAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: Person = Depends(require_admin),
):
    """Назначить сотрудника на рейс."""
    service = CrewService(db)
    try:
        return service.create_crew_assignment(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/assignments/{assignment_id}",
    response_model=DeleteResponse,
)
def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: Person = Depends(require_admin),
):
    """Удалить назначение сотрудника с рейса."""
    service = CrewService(db)
    try:
        return service.delete_crew_assignment(assignment_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении: {str(e)}")
