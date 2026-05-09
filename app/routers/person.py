"""Person router – basic CRUD operations for the Person model.

Endpoints:
* GET    /persons/               – list all persons
* GET    /persons/{person_id}    – retrieve a single person
* POST   /persons/               – create a new person
* PUT    /persons/{person_id}    – update an existing person
* DELETE /persons/{person_id}    – delete a person

The router uses the ``get_db`` dependency from ``dependencies.py`` to obtain a
SQLAlchemy ``Session``. All operations are performed synchronously because the
SQLAlchemy ORM in this project is used in the classic (non‑async) mode.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
import models  # импортируем файл models.py, где объявлен класс Person

router = APIRouter(prefix="/persons", tags=["Person"])

# Pydantic schemas for request/response payloads
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class PersonCreate(BaseModel):
    first_name: str = Field(..., max_length=30)
    last_name: str = Field(..., max_length=30)
    middle_name: Optional[str] = Field(None, max_length=30)
    phone: Optional[str] = Field(None, max_length=20)
    passport: str = Field(..., max_length=15)
    email: EmailStr = Field(..., max_length=100)
    password_hash: str = Field(..., max_length=255)


class PersonRead(PersonCreate):
    id: int

    class Config:
        orm_mode = True


@router.get("/", response_model=list[PersonRead])
def list_persons(db: Session = Depends(get_db)):
    return db.query(models.Person).all()


@router.get("/{person_id}", response_model=PersonRead)
def get_person(person_id: int, db: Session = Depends(get_db)):
    person = db.query(models.Person).filter(models.Person.id == person_id).first()
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Person not found"
        )
    return person


@router.post("/", response_model=PersonRead, status_code=status.HTTP_201_CREATED)
def create_person(payload: PersonCreate, db: Session = Depends(get_db)):
    # Проверяем уникальность email и passport
    if db.query(models.Person).filter(models.Person.email == payload.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    if (
        db.query(models.Person)
        .filter(models.Person.passport == payload.passport)
        .first()
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passport already registered",
        )

    person = models.Person(
        first_name=payload.first_name,
        last_name=payload.last_name,
        middle_name=payload.middle_name,
        phone=payload.phone,
        passport=payload.passport,
        email=payload.email,
        password_hash=payload.password_hash,
    )
    db.add(person)
    db.commit()
    db.refresh(person)
    return person


@router.put("/{person_id}", response_model=PersonRead)
def update_person(person_id: int, payload: PersonCreate, db: Session = Depends(get_db)):
    person = db.query(models.Person).filter(models.Person.id == person_id).first()
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Person not found"
        )
    # Обновляем поля
    for field, value in payload.model_dump().items():
        setattr(person, field, value)
    db.commit()
    db.refresh(person)
    return person


@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_person(person_id: int, db: Session = Depends(get_db)):
    person = db.query(models.Person).filter(models.Person.id == person_id).first()
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Person not found"
        )
    db.delete(person)
    db.commit()
    return None
