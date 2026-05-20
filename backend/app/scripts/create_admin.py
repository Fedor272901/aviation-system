#!/usr/bin/env python3
"""
Создание первого администратора в системе.
Запускать внутри контейнера:
    docker exec -it aviation-app python scripts/create_admin.py
Или локально:
    python scripts/create_admin.py
"""

import getpass
import sys
from sqlalchemy.orm import Session

# Добавляем корень проекта в PYTHONPATH
sys.path.insert(0, ".")

from app.db import SessionLocal
from app.crud.person import create_person, get_by_email, get_role_by_name
from app.models import SystemRole, PeopleSystemRole
from app.schemas.person import PersonCreate


def create_admin(db: Session) -> None:
    print("=" * 50)
    print("  Создание администратора Aviation System")
    print("=" * 50)

    email = input("Email: ").strip()
    if not email:
        print("❌ Email обязателен")
        return

    # Проверка существования
    existing = get_by_email(db, email)
    if existing:
        print(f"⚠️  Пользователь {email} уже существует (id={existing.id})")
        is_admin = any(r.role.role_name == "admin" for r in existing.system_roles)
        if is_admin:
            print("✅ Уже имеет роль admin")
        else:
            assign = input("Назначить роль admin? [y/N]: ").strip().lower()
            if assign == "y":
                admin_role = get_role_by_name(db, "admin")
                if not admin_role:
                    admin_role = SystemRole(role_name="admin")
                    db.add(admin_role)
                    db.commit()
                    db.refresh(admin_role)
                db.add(PeopleSystemRole(person_id=existing.id, role_id=admin_role.id))
                db.commit()
                print("✅ Роль admin назначена")
        return

    last_name = input("Фамилия: ").strip()
    first_name = input("Имя: ").strip()
    middle_name = input("Отчество (Enter пропустить): ").strip() or None
    phone = input("Телефон (Enter пропустить): ").strip() or None
    passport = input("Паспорт: ").strip()

    password = getpass.getpass("Пароль: ")
    password2 = getpass.getpass("Повторите пароль: ")
    if password != password2:
        print("❌ Пароли не совпадают")
        return
    if len(password) < 6:
        print("❌ Пароль должен быть не менее 6 символов")
        return

    # Создаём пользователя
    payload = PersonCreate(
        email=email,
        password=password,
        last_name=last_name,
        first_name=first_name,
        middle_name=middle_name,
        phone=phone,
        passport=passport,
    )
    user = create_person(db, payload)

    # Создаём/получаем роль admin
    admin_role = get_role_by_name(db, "admin")
    if not admin_role:
        admin_role = SystemRole(role_name="admin")
        db.add(admin_role)
        db.commit()
        db.refresh(admin_role)

    # Назначаем роль
    db.add(PeopleSystemRole(person_id=user.id, role_id=admin_role.id))
    db.commit()

    print(f"\n✅ Администратор успешно создан:")
    print(f"   ID:    {user.id}")
    print(f"   Email: {user.email}")
    print(f"   Роли:  admin")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        create_admin(db)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        raise
    finally:
        db.close()