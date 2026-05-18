
# Локальная разработка

## Вариант 1: Docker (рекомендуется)

```bash
cp .env.example .env
# Отредактировать .env
docker compose up -d
docker exec -it aviation-app python scripts/create_admin.py
docker compose logs -f app
```

## Вариант 2: Без Docker

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="mssql+pyodbc://..."
export SECRET_KEY="dev-secret-key-min-32-chars-long"
export DEBUG="true"
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

## Frontend dev

```bash
cd frontend
npm install
npm run dev  # http://localhost:5173
```

## Тесты

```bash
pytest -v
pytest --cov=app --cov-report=html
```