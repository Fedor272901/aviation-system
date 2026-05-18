# Архитектура

## Общая схема

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│   nginx     │────▶│   FastAPI   │
│  (React)    │◀────│  (80/443)   │◀────│   (8000)    │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                                │
                                         ┌──────▼──────┐
                                         │    MSSQL    │
                                         │   (1433)    │
                                         └─────────────┘
```

## Слои Backend

```
app/
├── main.py              # Точка входа
├── core/                # Конфиг, security, логи
├── db.py                # SQLAlchemy engine
├── models/              # ORM модели
├── schemas/             # Pydantic схемы
├── crud/                # CRUD операции
├── services/            # Бизнес-логика
├── routers/             # API endpoints
├── dependencies/        # Depends
├── middleware.py        # CORS
└── seed_data.py         # Справочники
```

## Ролевая модель

| Роль | Доступ |
|------|--------|
| `admin` | Полный CRUD |
| `user` | Просмотр рейсов, покупка билетов, профиль |
| `crew` | Управление экипажем |

## Жизненный цикл запроса

1. nginx → FastAPI
2. Router → Pydantic валидация
3. Service → бизнес-логика
4. CRUD → SQLAlchemy → MSSQL