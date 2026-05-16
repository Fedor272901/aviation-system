"""Тесты для HTTP API пользователей."""

import pytest
from fastapi.testclient import TestClient


class TestPersonAPI:
    """Тесты для API пользователей."""

    def test_create_person(self, client, test_person_data):
        """Создание пользователя через API."""
        response = client.post("/api/v1/persons/", json=test_person_data)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == test_person_data["email"]
        assert data["first_name"] == test_person_data["first_name"]
        assert "password" not in data

    def test_create_person_duplicate_email(self, client, test_person_data):
        """Создание пользователя с дублирующимся email через API."""
        client.post("/api/v1/persons/", json=test_person_data)

        response = client.post("/api/v1/persons/", json=test_person_data)

        assert response.status_code == 409
        assert "Email уже зарегистрирован" in response.json()["detail"]

    def test_get_person(self, client, test_person_data):
        """Получение пользователя через API."""
        create_response = client.post("/api/v1/persons/", json=test_person_data)
        person_id = create_response.json()["id"]

        response = client.get(f"/api/v1/persons/{person_id}")

        assert response.status_code == 200
        assert response.json()["id"] == person_id

    def test_get_person_not_found(self, client):
        """Получение несуществующего пользователя через API."""
        response = client.get("/api/v1/persons/9999")

        assert response.status_code == 404

    def test_get_all_persons(self, client, test_person_data):
        """Получение всех пользователей через API."""
        for i in range(3):
            data = test_person_data.copy()
            data["email"] = f"user{i}@example.com"
            data["passport"] = f"PASS{i}123456"
            client.post("/api/v1/persons/", json=data)

        response = client.get("/api/v1/persons/")

        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_update_person(self, client, test_person_data):
        """Обновление пользователя через API."""
        create_response = client.post("/api/v1/persons/", json=test_person_data)
        person_id = create_response.json()["id"]

        response = client.put(f"/api/v1/persons/{person_id}", json={
            "first_name": "Петр", "last_name": "Петров"
        })

        assert response.status_code == 200
        assert response.json()["first_name"] == "Петр"

    def test_change_password(self, client, test_person_data):
        """Смена пароля через API."""
        create_response = client.post("/api/v1/persons/", json=test_person_data)
        person_id = create_response.json()["id"]

        response = client.put(f"/api/v1/persons/{person_id}/password", json={
            "old_password": "Test1234!",
            "new_password": "NewPass123!"
        })

        assert response.status_code == 200

    def test_delete_person(self, client, test_person_data):
        """Удаление пользователя через API."""
        create_response = client.post("/api/v1/persons/", json=test_person_data)
        person_id = create_response.json()["id"]

        response = client.delete(f"/api/v1/persons/{person_id}")

        assert response.status_code == 200
        assert response.json()["deleted_id"] == person_id
