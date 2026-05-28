import os
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.crud.person import create_person, get_by_email, get_role_by_name
from app.models import SystemRole, PeopleSystemRole
from app.schemas.person import PersonCreate


def ensure_admin(db: Session) -> None:
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")

    if not email or not password:
        print("ℹ️ ADMIN_EMAIL/ADMIN_PASSWORD не заданы, пропускаем автосоздание admin")
        return

    first_name = os.getenv("ADMIN_FIRST_NAME", "Admin")
    last_name = os.getenv("ADMIN_LAST_NAME", "Root")
    middle_name = os.getenv("ADMIN_MIDDLE_NAME") or None
    phone = os.getenv("ADMIN_PHONE") or None
    passport = os.getenv("ADMIN_PASSPORT", "ADMIN000000000")

    user = get_by_email(db, email)
    if not user:
        payload = PersonCreate(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            phone=phone,
            passport=passport,
        )
        user = create_person(db, payload)
        print(f"✅ Создан admin-пользователь: {email}")
    else:
        print(f"ℹ️ Пользователь {email} уже существует")

    admin_role = get_role_by_name(db, "admin")
    if not admin_role:
        admin_role = SystemRole(role_name="admin")
        db.add(admin_role)
        db.commit()
        db.refresh(admin_role)

    already_admin = any(r.role_id == admin_role.id for r in user.system_roles)
    if not already_admin:
        db.add(PeopleSystemRole(person_id=user.id, role_id=admin_role.id))
        db.commit()
        print("✅ Роль admin назначена")
    else:
        print("ℹ️ Роль admin уже назначена")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        ensure_admin(db)
    finally:
        db.close()