# Backend API

## Базовый URL

- Локально: `http://localhost/api/v1`
- Production: `https://your-domain.ru/api/v1`

## Аутентификация

Все защищённые endpoints требуют заголовок:
```
Authorization: Bearer <token>
```

### Auth Endpoints

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/auth/register` | Регистрация (роль user) |
| POST | `/auth/login` | Вход, JWT |
| GET | `/auth/me` | Текущий пользователь |

### Основные Endpoints

| Метод | Путь | Доступ | Описание |
|-------|------|--------|----------|
| GET | `/flights/` | Все | Список рейсов |
| GET | `/flights/{id}` | Все | Рейс по ID |
| POST | `/flights/` | admin | Создать рейс |
| PUT | `/flights/{id}` | admin | Обновить рейс |
| DELETE | `/flights/{id}` | admin | Удалить рейс |
| POST | `/tickets/` | user | Купить билет |
| GET | `/persons/` | admin | Пользователи |

## Создание администратора

```bash
docker exec -it aviation-app python scripts/create_admin.py
```

## Коды ошибок

| Код | Значение |
|-----|----------|
| 422 | Ошибка валидации (Pydantic) |
| 401 | Не авторизован |
| 403 | Нет прав |
| 409 | Конфликт (email/паспорт уже есть) |

