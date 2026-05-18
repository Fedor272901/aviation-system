"""Seed-скрипт для заполнения базовых справочников."""

import logging
from sqlalchemy.orm import Session
from sqlalchemy import select
from decimal import Decimal

from app.models import (
    SystemRole,
    FlightStatus,
    TicketStatus,
    SeatClass,
)

logger = logging.getLogger(__name__)


def seed_database(db: Session) -> None:
    """Заполняет базу данных базовыми справочниками, если они отсутствуют."""

    # --- Системные роли ---
    roles = ["admin", "user", "crew"]
    for role_name in roles:
        existing = db.scalar(select(SystemRole).where(SystemRole.role_name == role_name))
        if not existing:
            db.add(SystemRole(role_name=role_name))
            logger.info(f"Создана системная роль: {role_name}")

    # --- Статусы рейсов ---
    flight_statuses = [
        "Планируется", "Регистрация", "Посадка",
        "Вылетел", "Прибыл", "Отменён", "Задержан",
    ]
    for status_name in flight_statuses:
        existing = db.scalar(
            select(FlightStatus).where(FlightStatus.status_name == status_name)
        )
        if not existing:
            db.add(FlightStatus(status_name=status_name))
            logger.info(f"Создан статус рейса: {status_name}")

    # --- Статусы билетов ---
    ticket_statuses = ["Подтверждён", "Отменён", "Использован", "Возвращён"]
    for status_name in ticket_statuses:
        existing = db.scalar(
            select(TicketStatus).where(TicketStatus.status_name == status_name)
        )
        if not existing:
            db.add(TicketStatus(status_name=status_name))
            logger.info(f"Создан статус билета: {status_name}")

    # --- Классы мест ---
    seat_classes = [
        {"name": "Эконом", "multiplier": Decimal("1.00"), "desc": "Стандартный класс"},
        {"name": "Бизнес", "multiplier": Decimal("2.50"), "desc": "Бизнес-класс"},
        {"name": "Первый", "multiplier": Decimal("5.00"), "desc": "Первый класс"},
    ]
    for sc in seat_classes:
        existing = db.scalar(
            select(SeatClass).where(SeatClass.class_name == sc["name"])
        )
        if not existing:
            db.add(SeatClass(
                class_name=sc["name"],
                price_multiplier=sc["multiplier"],
                description=sc["desc"],
            ))
            logger.info(f"Создан класс мест: {sc['name']}")

    db.commit()
    logger.info("Справочники успешно проверены/заполнены")


def seed_dev_data(db: Session) -> None:
    """
    Тестовые данные ТОЛЬКО для локальной разработки.
    НЕ вызывать в production.
    """
    from app.models import Airport, Airline

    airports = [
        {"code": "SVO", "name": "Шереметьево", "city": "Москва"},
        {"code": "LED", "name": "Пулково", "city": "Санкт-Петербург"},
        {"code": "VKO", "name": "Внуково", "city": "Москва"},
        {"code": "AER", "name": "Сочи", "city": "Сочи"},
    ]
    for ap in airports:
        existing = db.scalar(select(Airport).where(Airport.code == ap["code"]))
        if not existing:
            db.add(Airport(**ap))
            logger.info(f"Создан аэропорт: {ap['code']}")

    airlines = [
        {"name": "Аэрофлот", "code": "SU", "country": "Россия"},
        {"name": "Победа", "code": "DP", "country": "Россия"},
        {"name": "S7 Airlines", "code": "S7", "country": "Россия"},
    ]
    for al in airlines:
        existing = db.scalar(select(Airline).where(Airline.code == al["code"]))
        if not existing:
            db.add(Airline(**al))
            logger.info(f"Создана авиакомпания: {al['code']}")

    db.commit()
    logger.info("Тестовые данные успешно проверены/заполнены")