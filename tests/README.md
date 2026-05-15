# Тесты для Aviation System

## Структура тестов

```
tests/
├── __init__.py
├── conftest.py              # Общие фикстуры
├── pytest.ini               # Конфигурация pytest
├── README.md                # Документация тестов
├── test_person_service.py   # Тесты сервиса Person
├── test_flight_service.py   # Тесты сервиса Flight
├── test_aircraft_service.py # Тесты сервиса Aircraft
├── test_ticket_service.py   # Тесты сервиса Ticket
├── test_crud.py             # Тесты CRUD операций
├── test_api_person.py       # Тесты HTTP API для пользователей
└── test_api_flight.py       # Тесты HTTP API для рейсов
```

## Запуск тестов

### Запустить все тесты

```bash
pytest
```

### Запустить с подробным выводом

```bash
pytest -v
```

### Запустить только сервисные тесты

```bash
pytest tests/test_*_service.py -v
```

### Запустить только API тесты

```bash
pytest tests/test_api_*.py -v
```

### Запустить только CRUD тесты

```bash
pytest tests/test_crud.py -v
```

### Запустить конкретный тест

```bash
pytest tests/test_person_service.py::TestPersonServiceCreate::test_create_person_success -v
```

### Запустить с покрытием кода

```bash
pytest --cov=app --cov-report=term-missing
```

### Запустить с HTML отчётом о покрытии

```bash
pytest --cov=app --cov-report=html
```

После выполнения откройте `htmlcov/index.html` в браузере.

### Запустить тесты с минимальным покрытием 90%

```bash
pytest --cov=app --cov-fail-under=90
```

## Целевое покрытие

- Сервисный слой: 90%+
- CRUD слой: 85%+
- API слой: 80%+
- **Общее покрытие: 90%**

## Типы тестов

### 1. Сервисные тесты (test_*_service.py)
Тестируют бизнес-логику сервисного слоя:
- Валидация входных данных
- Проверка бизнес-правил
- Обработка ошибок

### 2. CRUD тесты (test_crud.py)
Тестируют операции с базой данных:
- CREATE, READ, UPDATE, DELETE
- Подсчёт записей
- Поиск и фильтрация

### 3. API тесты (test_api_*.py)
Тестируют HTTP эндпоинты:
- HTTP статус коды
- Формат ответов
- Валидация запросов

## Фикстуры

### Общие фикстуры (conftest.py)

- `test_engine` - Тестовая БД SQLite в памяти
- `test_db` - Сессия БД для каждого теста
- `client` - Тестовый HTTP клиент FastAPI
- `test_person_data` - Тестовые данные пользователя
- `test_airport_data` - Тестовые данные аэропорта
- `test_airline_data` - Тестовые данные авиакомпании
- `test_flight_status_data` - Тестовые данные статуса
- `test_seat_class_data` - Тестовые данные класса мест
- `test_model_aircraft_data` - Тестовые данные модели самолёта
- `test_aircraft_data` - Тестовые данные самолёта

## Добавление новых тестов

### Для сервиса

```python
class TestMyService:
    def test_my_method_success(self, my_service, test_data):
        """Успешное выполнение метода."""
        result = my_service.my_method(test_data)
        
        assert result is not None
        assert result.some_field == expected_value
```

### Для CRUD

```python
class TestMyCRUD:
    def test_create_success(self, test_db):
        """Успешное создание записи."""
        payload = MySchema(...)
        result = my_crud.create(test_db, payload)
        
        assert result.id is not None
```

### Для API

```python
class TestMyAPI:
    def test_create_endpoint(self, client, test_data):
        """Создание через API."""
        response = client.post("/api/v1/my-endpoint/", json=test_data)
        
        assert response.status_code == 201
        assert response.json()["id"] is not None
```

## Решение проблем

### Тесты падают с ошибкой импорта

```bash
# Убедитесь, что вы в корне проекта
cd /home/fgrek/dev/fastapi-app

# Установите зависимости
pip install -r requirements-test.txt
```

### Ошибка подключения к БД

Все тесты используют SQLite в памяти, внешняя БД не требуется.

### Низкое покрытие кода

Запустите тесты с флагом `--cov` и посмотрите отчёт:

```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

## CI/CD интеграция

Пример конфигурации для GitHub Actions:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      - name: Run tests
        run: pytest --cov=app --cov-fail-under=90
```
