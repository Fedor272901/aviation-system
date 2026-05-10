from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app import models
from app.schemas.person import PersonRead, PersonCreate

router = APIRouter(prefix="/persons", tags=["Person"])


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
    data = payload.model_dump(exclude={"password"})

    for field, value in data.items():
        setattr(person, field, value)

    person.password_hash = payload.password
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
