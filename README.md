# ✈️ Aviation System

Система управления авиаперевозками. Fullstack-приложение на **FastAPI** + **React** + **MSSQL**.

## 🚀 Быстрый старт

```bash
git clone <repo-url>
cd fastapi-app
cp .env.example .env
# Отредактируй .env
docker compose up -d
docker exec -it aviation-app python scripts/create_admin.py
# Открой http://localhost
```

## 📚 Документация

| Документ | Описание |
|----------|----------|
| [docs/architecture.md](docs/architecture.md) | Архитектура и стек технологий |
| [docs/backend.md](docs/backend.md) | API endpoints, авторизация, роли |
| [docs/frontend.md](docs/frontend.md) | React-приложение, роутинг, компоненты |
| [docs/database.md](docs/database.md) | Схема БД, миграции, seed-данные |
| [docs/deployment.md](docs/deployment.md) | Деплой в Yandex Cloud |
| [docs/local-development.md](docs/local-development.md) | Локальная разработка |
| [docs/security.md](docs/security.md) | Безопасность, JWT, 152-ФЗ |
| [docs/testing.md](docs/testing.md) | Запуск тестов |
| [docs/troubleshooting.md](docs/troubleshooting.md) | Решение проблем |

## 🏗️ Технологический стек

**Backend:** Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic, MSSQL 2022, pyodbc
**Frontend:** React 18, TypeScript, Vite, Zustand, Axios
**Инфраструктура:** Docker, Docker Compose, nginx, certbot

## 🔐 Безопасность

JWT + роли (admin/user/crew), bcrypt, rate limiting, HTTPS.

## 📄 Лицензия

MIT