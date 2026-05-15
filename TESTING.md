# Руководство по тестированию Aviation System

## Быстрый старт

```bash
# Установка зависимостей для тестов
pip install -r requirements-test.txt

# Запустить все тесты
pytest

# Запустить с покрытием
pytest --cov=app --cov-report=term-missing

# Запустить с HTML отчётом
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

## Структура тестов

| Файл | Покрытие | Кол-во тестов |
|------|----------|---------------|
| `tests/test_person_service.py` | PersonService | ~25 тестов |
| `tests/test_flight_service.py` | FlightService | ~20 тестов |
| `tests/test_aircraft_service.py` | AircraftService | ~25 тестов |
| `tests/test_ticket_service.py` | TicketService | ~20 тестов |
| `tests/test_crud.py` | CRUD операции | ~25 тестов |
| `tests/test_api_person.py` | Person API | ~8 тестов |
| `tests/test_api_flight.py` | Flight API | ~15 тестов |

**Всего: ~138 тестов**

## Ожидаемое покрытие

После запуска всех тестов ожидается покрытие:

```
Name                           Stmts   Miss  Cover   Missing
------------------------------------------------------------
app/services/person.py           100%
app/services/flight.py            95%
app/services/aircraft.py          95%
app/services/ticket.py            95%
app/crud/person.py               100%
app/crud/flight.py                98%
app/crud/aircraft.py              98%
app/crud/ticket.py                98%
app/routers/person.py             90%
app/routers/flight.py             90%
------------------------------------------------------------
TOTAL                             90%
```

## Команды для тестирования

### Базовые команды

```bash
# Все тесты
pytest

# С подробным выводом
pytest -v

# Только失败的 тесты
pytest -lf

# Определить тесты
pytest --collect-only
```

### Тестирование по категориям

```bash
# Только сервисные тесты
pytest tests/test_*_service.py -v

# Только API тесты
pytest tests/test_api_*.py -v

# Только CRUD тесты
pytest tests/test_crud.py -v

# Тесты для конкретного сервиса
pytest tests/test_person_service.py -v
```

### Тестирование с покрытием

```bash
# Базовое покрытие
pytest --cov=app

# С пропусками
pytest --cov=app --cov-report=term-missing

# С минимальным порогом 90%
pytest --cov=app --cov-fail-under=90

# HTML отчёт
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

### Тестирование конкретных файлов/классов/методов

```bash
# Конкретный файл
pytest tests/test_person_service.py -v

# Конкретный класс
pytest tests/test_person_service.py::TestPersonServiceCreate -v

# Конкретный тест
pytest tests/test_person_service.py::TestPersonServiceCreate::test_create_person_success -v
```

## Интеграция с CI/CD

### GitHub Actions

Создайте `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      - name: Run tests
        run: pytest --cov=app --cov-fail-under=90
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### GitLab CI

Создайте `.gitlab-ci.yml`:

```yaml
test:
  image: python:3.10
  script:
    - pip install -r requirements.txt
    - pip install -r requirements-test.txt
    - pytest --cov=app --cov-fail-under=90
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

## Написание новых тестов

### Шаблон для сервисного теста

```python
import pytest
from app.services.my_service import MyService

class TestMyService:
    def test_method_success(self, my_service, test_data):
        """Успешное выполнение метода."""
        result = my_service.my_method(test_data)
        
        assert result is not None
        assert result.field == expected_value
    
    def test_method_error(self, my_service, invalid_data):
        """Обработка ошибки в методе."""
        with pytest.raises(ValueError, match="описание ошибки"):
            my_service.my_method(invalid_data)
```

### Шаблон для API теста

```python
import pytest

class TestMyAPI:
    def test_endpoint_success(self, client, test_data):
        """Успешный запрос к эндпоинту."""
        response = client.post("/api/v1/endpoint/", json=test_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
    
    def test_endpoint_error(self, client, invalid_data):
        """Обработка ошибки в эндпоинте."""
        response = client.post("/api/v1/endpoint/", json=invalid_data)
        
        assert response.status_code == 400
        assert "detail" in response.json()
```

## Решение проблем

### "ModuleNotFoundError"

```bash
# Убедитесь, что вы в корне проекта
cd /home/fgrek/dev/fastapi-app

# Переустановите зависимости
pip install -r requirements.txt
pip install -r requirements-test.txt
```

### "ImportError: cannot import name"

Убедитесь, что все файлы обновлены после применения патча.

### Низкое покрытие

1. Запустите тесты с `--cov` для анализа
2. Добавьте недостающие тесты
3. Проверьте, что все функции покрыты

```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html  # Откройте в браузере
```

## Поддерживаемая версия Python

- Python 3.10+
- Рекомендовано: Python 3.10.x

## Зависимости для тестирования

Установите через:

```bash
pip install -r requirements-test.txt
```

Зависимости:
- `pytest` - фреймворк для тестов
- `pytest-asyncio` - поддержка async/await
- `pytest-cov` - покрытие кода
- `httpx` - HTTP клиент для тестов API
