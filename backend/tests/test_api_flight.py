"""Тесты для HTTP API рейсов."""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone


class TestAirportAPI:
    """Тесты для API аэропортов."""

    def test_create_airport(self, client, admin_headers, test_airport_data):
        """Создание аэропорта через API."""
        response = client.post(
            "/api/v1/flights/airports/",
            json=test_airport_data,
            headers=admin_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["code"] == "SVO"
        assert data["city"] == "Москва"

    def test_create_airport_duplicate_code(
        self, client, admin_headers, test_airport_data
    ):
        """Создание аэропорта с дублирующимся кодом через API."""
        client.post(
            "/api/v1/flights/airports/",
            json=test_airport_data,
            headers=admin_headers,
        )

        response = client.post(
            "/api/v1/flights/airports/",
            json=test_airport_data,
            headers=admin_headers,
        )
        assert response.status_code == 409

    def test_get_airport(self, client, admin_headers, test_airport_data):
        """Получение аэропорта через API."""
        create_response = client.post(
            "/api/v1/flights/airports/",
            json=test_airport_data,
            headers=admin_headers,
        )
        airport_id = create_response.json()["id"]

        response = client.get(f"/api/v1/flights/airports/{airport_id}")
        assert response.status_code == 200

    def test_get_all_airports(self, client, admin_headers, test_airport_data):
        """Получение всех аэропортов через API."""
        for code, city in [("SVO", "Москва"), ("LED", "СПб"), ("VKO", "Внуково")]:
            client.post(
                "/api/v1/flights/airports/",
                json={"code": code, "name": f"Аэропорт {city}", "city": city},
                headers=admin_headers,
            )

        response = client.get("/api/v1/flights/airports/")
        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_delete_airport(self, client, admin_headers, test_airport_data):
        """Удаление аэропорта через API."""
        create_response = client.post(
            "/api/v1/flights/airports/",
            json=test_airport_data,
            headers=admin_headers,
        )
        airport_id = create_response.json()["id"]

        response = client.delete(
            f"/api/v1/flights/airports/{airport_id}",
            headers=admin_headers,
        )
        assert response.status_code == 200


class TestAirlineAPI:
    """Тесты для API авиакомпаний."""

    def test_create_airline(self, client, admin_headers, test_airline_data):
        """Создание авиакомпании через API."""
        response = client.post(
            "/api/v1/flights/airlines/",
            json=test_airline_data,
            headers=admin_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["code"] == "SU"

    def test_get_all_airlines(self, client, admin_headers, test_airline_data):
        """Получение всех авиакомпаний через API."""
        client.post(
            "/api/v1/flights/airlines/",
            json=test_airline_data,
            headers=admin_headers,
        )
        client.post(
            "/api/v1/flights/airlines/",
            json={"name": "Победа", "code": "DP", "country": "Россия"},
            headers=admin_headers,
        )

        response = client.get("/api/v1/flights/airlines/")
        assert response.status_code == 200
        assert len(response.json()) == 2


class TestFlightStatusAPI:
    """Тесты для API статусов рейсов."""

    def test_create_flight_status(
        self, client, admin_headers, test_flight_status_data
    ):
        """Создание статуса через API."""
        response = client.post(
            "/api/v1/flights/statuses/",
            json=test_flight_status_data,
            headers=admin_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status_name"] == "Планируется"

    def test_get_all_flight_statuses(
        self, client, admin_headers, test_flight_status_data
    ):
        """Получение всех статусов через API."""
        client.post(
            "/api/v1/flights/statuses/",
            json=test_flight_status_data,
            headers=admin_headers,
        )
        client.post(
            "/api/v1/flights/statuses/",
            json={"status_name": "Выполняется"},
            headers=admin_headers,
        )

        response = client.get("/api/v1/flights/statuses/")
        assert response.status_code == 200
        assert len(response.json()) == 2


class TestFlightAPI:
    """Тесты для API рейсов."""

    @pytest.fixture
    def setup_flight_data(self, client, admin_headers):
        """Создаёт базовые данные для тестов рейсов."""
        airport1 = client.post(
            "/api/v1/flights/airports/",
            json={"code": "SVO", "name": "Шереметьево", "city": "Москва"},
            headers=admin_headers,
        ).json()
        airport2 = client.post(
            "/api/v1/flights/airports/",
            json={"code": "LED", "name": "Пулково", "city": "СПб"},
            headers=admin_headers,
        ).json()
        airline = client.post(
            "/api/v1/flights/airlines/",
            json={"name": "Аэрофлот", "code": "SU", "country": "Россия"},
            headers=admin_headers,
        ).json()
        status = client.post(
            "/api/v1/flights/statuses/",
            json={"status_name": "Планируется"},
            headers=admin_headers,
        ).json()

        seat_class = client.post(
            "/api/v1/aircraft/seat-classes/",
            json={
                "class_name": "Эконом",
                "price_multiplier": 1.0,
                "description": "Эконом",
            },
            headers=admin_headers,
        ).json()

        model = client.post(
            "/api/v1/aircraft/models/",
            json={
                "name": "Boeing 737",
                "manufacturer": "Boeing",
                "seats": [{"class_id": seat_class["id"], "count": 150}],
            },
            headers=admin_headers,
        ).json()

        aircraft = client.post(
            "/api/v1/aircraft/",
            json={
                "registration_number": "RA-12345",
                "id_model": model["id"],
                "manufacture_year": 2020,
                "last_maintenance": "2024-01-01",
            },
            headers=admin_headers,
        ).json()

        return {
            "airport1": airport1,
            "airport2": airport2,
            "airline": airline,
            "status": status,
            "aircraft": aircraft,
        }

    def test_create_flight(self, client, admin_headers, setup_flight_data):
        """Создание рейса через API."""
        payload = {
            "flight_number": "SU100",
            "departure_datetime": (
                datetime.now(timezone.utc) + timedelta(days=1)
            ).isoformat(),
            "arrival_datetime": (
                datetime.now(timezone.utc) + timedelta(days=1, hours=2)
            ).isoformat(),
            "id_from": setup_flight_data["airport1"]["id"],
            "id_to": setup_flight_data["airport2"]["id"],
            "id_airline": setup_flight_data["airline"]["id"],
            "id_aircraft": setup_flight_data["aircraft"]["id"],
            "id_status": setup_flight_data["status"]["id"],
        }

        response = client.post(
            "/api/v1/flights/", json=payload, headers=admin_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["flight_number"] == "SU100"

    def test_create_flight_past_datetime(
        self, client, admin_headers, setup_flight_data
    ):
        """Создание рейса в прошлом через API."""
        payload = {
            "flight_number": "SU100",
            "departure_datetime": (
                datetime.now(timezone.utc) - timedelta(days=1)
            ).isoformat(),
            "arrival_datetime": datetime.now(timezone.utc).isoformat(),
            "id_from": setup_flight_data["airport1"]["id"],
            "id_to": setup_flight_data["airport2"]["id"],
            "id_airline": setup_flight_data["airline"]["id"],
            "id_aircraft": setup_flight_data["aircraft"]["id"],
            "id_status": setup_flight_data["status"]["id"],
        }

        response = client.post(
            "/api/v1/flights/", json=payload, headers=admin_headers
        )
        assert response.status_code == 400

    def test_get_all_flights(self, client, admin_headers, setup_flight_data):
        """Получение всех рейсов через API."""
        payload = {
            "flight_number": "SU100",
            "departure_datetime": (
                datetime.now(timezone.utc) + timedelta(days=1)
            ).isoformat(),
            "arrival_datetime": (
                datetime.now(timezone.utc) + timedelta(days=1, hours=2)
            ).isoformat(),
            "id_from": setup_flight_data["airport1"]["id"],
            "id_to": setup_flight_data["airport2"]["id"],
            "id_airline": setup_flight_data["airline"]["id"],
            "id_aircraft": setup_flight_data["aircraft"]["id"],
            "id_status": setup_flight_data["status"]["id"],
        }

        client.post(
            "/api/v1/flights/", json=payload, headers=admin_headers
        )

        response = client.get("/api/v1/flights/")
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_search_flights(self, client, admin_headers, setup_flight_data):
        """Поиск рейсов через API."""
        payload = {
            "flight_number": "SU100",
            "departure_datetime": (
                datetime.now(timezone.utc) + timedelta(days=1)
            ).isoformat(),
            "arrival_datetime": (
                datetime.now(timezone.utc) + timedelta(days=1, hours=2)
            ).isoformat(),
            "id_from": setup_flight_data["airport1"]["id"],
            "id_to": setup_flight_data["airport2"]["id"],
            "id_airline": setup_flight_data["airline"]["id"],
            "id_aircraft": setup_flight_data["aircraft"]["id"],
            "id_status": setup_flight_data["status"]["id"],
        }

        client.post(
            "/api/v1/flights/", json=payload, headers=admin_headers
        )

        response = client.post(
            "/api/v1/flights/search/",
            json={"id_from": setup_flight_data["airport1"]["id"]},
        )
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_delete_flight(self, client, admin_headers, setup_flight_data):
        """Удаление рейса через API."""
        payload = {
            "flight_number": "SU100",
            "departure_datetime": (
                datetime.now(timezone.utc) + timedelta(days=1)
            ).isoformat(),
            "arrival_datetime": (
                datetime.now(timezone.utc) + timedelta(days=1, hours=2)
            ).isoformat(),
            "id_from": setup_flight_data["airport1"]["id"],
            "id_to": setup_flight_data["airport2"]["id"],
            "id_airline": setup_flight_data["airline"]["id"],
            "id_aircraft": setup_flight_data["aircraft"]["id"],
            "id_status": setup_flight_data["status"]["id"],
        }

        create_response = client.post(
            "/api/v1/flights/", json=payload, headers=admin_headers
        )
        flight_id = create_response.json()["id"]

        response = client.delete(
            f"/api/v1/flights/{flight_id}", headers=admin_headers
        )
        assert response.status_code == 200