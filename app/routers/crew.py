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
from app import crud
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
    return crud.crew.get_all_flight_roles(db)


@router.post(
    "/roles/",
    response_model=FlightRoleRead,
    status_code=status.HTTP_201_CREATED,
)
def create_flight_role(payload: FlightRoleCreate, db: Session = Depends(get_db)):
    """Создать новую должность."""
    try:
        return crud.crew.create_flight_role(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/roles/{role_id}",
    response_model=DeleteResponse,
)
def delete_flight_role(role_id: int, db: Session = Depends(get_db)):
    """Удалить должность."""
    role = crud.crew.get_flight_role(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Должность не найдена"
        )

    try:
        return crud.crew.delete_flight_role(db, role)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка при удалении: {str(e)}"
        )


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
    return crud.crew.get_all_crew(db, skip=skip, limit=limit)


@router.get("/{crew_id}", response_model=CrewRead)
def get_crew(crew_id: int, db: Session = Depends(get_db)):
    """Получить сотрудника по ID."""
    crew = crud.crew.get_crew(db, crew_id)
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
def create_crew(payload: CrewCreate, db: Session = Depends(get_db)):
    """Создать нового сотрудника экипажа."""
    try:
        return crud.crew.create_crew(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{crew_id}", response_model=CrewRead)
def update_crew(crew_id: int, payload: CrewCreate, db: Session = Depends(get_db)):
    """Обновить данные сотрудника."""
    crew = crud.crew.get_crew(db, crew_id)
    if not crew:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Сотрудник не найден"
        )

    try:
        return crud.crew.update_crew(db, crew, payload.person_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{crew_id}", response_model=DeleteResponse)
def delete_crew(crew_id: int, db: Session = Depends(get_db)):
    """Удалить сотрудника из экипажа."""
    crew = crud.crew.get_crew(db, crew_id)
    if not crew:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Сотрудник не найден"
        )

    try:
        return crud.crew.delete_crew(db, crew)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка при удалении: {str(e)}"
        )


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
    return crud.crew.get_all_crew_assignments(db, skip=skip, limit=limit)


@router.get(
    "/assignments/flight/{flight_id}",
    response_model=List[CrewAssignmentRead],
)
def get_assignments_by_flight(
    flight_id: int,
    db: Session = Depends(get_db),
):
    """Получить всех сотрудников, назначенных на рейс."""
    return crud.crew.get_assignments_by_flight(db, flight_id)


@router.get(
    "/assignments/crew/{crew_id}",
    response_model=List[CrewAssignmentRead],
)
def get_assignments_by_crew(
    crew_id: int,
    db: Session = Depends(get_db),
):
    """Получить все назначения сотрудника."""
    return crud.crew.get_assignments_by_crew(db, crew_id)


@router.post(
    "/assignments/",
    response_model=CrewAssignmentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_assignment(payload: CrewAssignmentCreate, db: Session = Depends(get_db)):
    """Назначить сотрудника на рейс."""
    try:
        return crud.crew.create_crew_assignment(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/assignments/{assignment_id}",
    response_model=DeleteResponse,
)
def delete_assignment(assignment_id: int, db: Session = Depends(get_db)):
    """Удалить назначение сотрудника с рейса."""
    assignment = crud.crew.get_crew_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Назначение не найдено"
        )

    try:
        return crud.crew.delete_crew_assignment(db, assignment)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка при удалении: {str(e)}"
        )