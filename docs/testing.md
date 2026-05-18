# Тестирование

## Backend

```bash
pytest -v
pytest --cov=app --cov-report=html --cov-report=term
pytest tests/test_person_service.py -v
```

## Структура

```
tests/
├── conftest.py
├── test_crud/
├── test_services/
│   ├── test_flight_service.py
│   ├── test_person_service.py
│   ├── test_aircraft_service.py
│   └── test_ticket_service.py
└── test_api/
```

## Frontend

E2E тесты не настроены. Рекомендуется Playwright.