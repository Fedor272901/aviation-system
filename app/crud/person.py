# app/crud/person.py
from sqlalchemy.orm import Session
from app.models import Person
from app.schemas.person import PersonCreate
from app.auth.hashing import hash_password


def get_person(db: Session, person_id: int) -> Person | None:
    return db.query(Person).filter(Person.id == person_id).first()


def get_by_email(db: Session, email: str) -> Person | None:
    return db.query(Person).filter(Person.email == email).first()


def get_by_passport(db: Session, passport: str) -> Person | None:
    return db.query(Person).filter(Person.passport == passport).first()


def create_person(db: Session, payload: PersonCreate) -> Person:
    person = Person(
        first_name=payload.first_name,
        last_name=payload.last_name,
        middle_name=payload.middle_name,
        phone=payload.phone,
        passport=payload.passport,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(person)
    db.commit()
    db.refresh(person)
    return person


def update_person(db: Session, person: Person, payload: PersonCreate) -> Person:
    for field in [
        "first_name",
        "last_name",
        "middle_name",
        "phone",
        "passport",
        "email",
    ]:
        setattr(person, field, getattr(payload, field))
    person.password_hash = hash_password(payload.password)
    db.commit()
    db.refresh(person)
    return person


def delete_person(db: Session, person: Person) -> None:
    db.delete(person)
    db.commit()
