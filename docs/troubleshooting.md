
# Решение проблем

## Login timeout expired

Причина: MSSQL ещё не готов.

Решение: подождать, `docker-entrypoint.sh` делает 30 попыток.

## Вопросительные знаки вместо кириллицы

Причина: коллация `SQL_Latin1_General_CP1_CI_AS`.

Решение:
```bash
docker compose down
docker volume rm fastapi-app_mssql_data
docker compose up -d --build
```

## 403 Forbidden

Причина: nginx не находит `index.html`.

Решение: проверить `dist/` внутри образа.

## npm run build падает

Причина: TS6133 неиспользуемые переменные.

Решение: удалить неиспользуемые импорты.

## CREATE DATABASE в транзакции

Причина: SQLAlchemy открывает транзакцию.

Решение: в `docker-entrypoint.sh` используется `pyodbc` с `autocommit=True`.