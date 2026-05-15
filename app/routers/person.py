from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app import models, crud
from app.schemas.person import PersonRead, PersonCreate

router = APIRouter(prefix="/persons", tags=["Person"])


@router.get("/", response_model=list[PersonRead])
def list_persons(db: Session = Depends(get_db)):
    return db.query(models.Person).all()


@router.get("/{person_id}", response_model=PersonRead)
def get_person(person_id: int, db: Session = Depends(get_db)):
    person = crud.person.get_person(db, person_id)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Person not found"
        )
    return person


@router.post("/", response_model=PersonRead, status_code=status.HTTP_201_CREATED)
def create_person(payload: PersonCreate, db: Session = Depends(get_db)):
    # Проверяем уникальность email и passport
    if crud.person.get_by_email(db, payload.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if crud.person.get_by_passport(db, payload.passport):
        raise HTTPException(status_code=400, detail="Passport already registered")
    return crud.person.create_person(db, payload)


@router.put("/{person_id}", response_model=PersonRead)
def update_person(person_id: int, payload: PersonCreate, db: Session = Depends(get_db)):
    person = crud.person.get_person(db, person_id)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Person not found"
        )
    # Обновляем поля
    return crud.person.update_person(db, person, payload)


@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_person(person_id: int, db: Session = Depends(get_db)):
    person = crud.person.get_person(db, person_id)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Person not found"
        )
    crud.person.delete_person(db, person)
    return None
