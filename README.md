# Aviation System

Система для управления авиаперевозками.

Проект делал в основном с упором на backend, базу данных и Docker.

## Стек

**Backend**

* Python
* FastAPI
* SQLAlchemy
* Alembic
* Pydantic
* JWT

**Database**

* Microsoft SQL Server

**Frontend**

* React
* TypeScript

**Infrastructure**

* Docker
* Docker Compose
* Nginx
* GitHub Actions

## Что реализовано

* регистрация и авторизация пользователей
* JWT-аутентификация
* роли пользователей
* работа с рейсами
* самолёты и аэропорты
* экипажи
* покупка билетов
* CRUD для основных сущностей
* работа с базой данных через SQLAlchemy
* миграции Alembic
* REST API на FastAPI
* Docker-сборка и запуск проекта

## Архитектура

```text
React
  ↓
Nginx
  ↓
FastAPI
  ↓
SQL Server
```

## Запуск

```bash
git clone git@github.com:Fedor272901/aviation-system.git
cd aviation-system
cp .env.example .env
```

Настроить `.env`, затем:

```bash
docker compose up -d --build
```

После запуска:

* http://localhost

## Скриншоты

<img width="1763" height="909" alt="image" src="https://github.com/user-attachments/assets/00f9c894-e51d-4076-ae8e-073177db0df1" />
<img width="1772" height="733" alt="image" src="https://github.com/user-attachments/assets/75b37924-c229-4202-8080-dc8e4794397b" />
<img width="1785" height="661" alt="image" src="https://github.com/user-attachments/assets/f6f27ef3-bd5f-4f94-8fb2-90abc34c231a" />
<img width="1785" height="661" alt="image" src="https://github.com/user-attachments/assets/e05e9f9c-3bfd-47d4-947f-c0cff6522282" />
<img width="1746" height="506" alt="image" src="https://github.com/user-attachments/assets/b6f1e68f-98c9-4eaf-a442-48dcfc7133d0" />


## Статус

Учебный проект.
