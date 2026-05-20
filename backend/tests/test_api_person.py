"""Тесты для HTTP API пользователей."""

import pytest
from fastapi.testclient import TestClient


class TestPersonAPI:
    """Тесты для API пользователей."""

    def test_create_person(self, client, auth_headers):
        """Создание пользователя через API (требуется авторизация)."""
        payload = {
            "first_name": "Иван",
            "last_name": "Иванов",
            "middle_name": "Иванович",
            "phone": "+79001234567",
            "passport": "1234567890",
            "email": "ivan@example.com",
            "password": "Test1234!",
        }
        response = client.post("/api/v1/persons/", json=payload, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == payload["email"]
        assert "password" not in data

    def test_create_person_duplicate_email(self, client, auth_headers):
        """Создание пользователя с дублирующимся email через API."""
        payload = {
            "first_name": "Иван",
            "last_name": "Иванов",
            "middle_name": "Иванович",
            "phone": "+79001234567",
            "passport": "1234567890",
            "email": "ivan2@example.com",
            "password": "Test1234!",
        }
        client.post("/api/v1/persons/", json=payload, headers=auth_headers)

        response = client.post("/api/v1/persons/", json=payload, headers=auth_headers)
        assert response.status_code == 409
        assert "Email уже зарегистрирован" in response.json()["detail"]

    def test_get_person(self, client):
        """Получение своего профиля через API."""
        payload = {
            "first_name": "Иван",
            "last_name": "Иванов",
            "middle_name": "Иванович",
            "phone": "+79001234567",
            "passport": "GET1234567",
            "email": "getself@example.com",
            "password": "Test1234!",
        }
        reg = client.post("/api/v1/auth/register", json=payload)
        assert reg.status_code == 200
        person_id = reg.json()["id"]

        login = client.post(
            "/api/v1/auth/login",
            json={"email": "getself@example.com", "password": "Test1234!"},
        )
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(f"/api/v1/persons/{person_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["id"] == person_id

    def test_get_person_not_found(self, client, auth_headers):
        """Получение чужого/несуществующего пользователя — 403."""
        response = client.get("/api/v1/persons/9999", headers=auth_headers)
        assert response.status_code == 403

    def test_get_all_persons(self, client, admin_headers):
        """Получение всех пользователей через API (только admin)."""
        response = client.get("/api/v1/persons/", headers=admin_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_all_persons_forbidden_for_user(self, client, auth_headers):
        """Обычный пользователь не может получить список всех пользователей."""
        response = client.get("/api/v1/persons/", headers=auth_headers)
        assert response.status_code == 403

    def test_update_person(self, client):
        """Обновление своего профиля через API."""
        payload = {
            "first_name": "Иван",
            "last_name": "Иванов",
            "middle_name": "Иванович",
            "phone": "+79001234567",
            "passport": "UPD1234567",
            "email": "updateself@example.com",
            "password": "Test1234!",
        }
        reg = client.post("/api/v1/auth/register", json=payload)
        assert reg.status_code == 200
        person_id = reg.json()["id"]

        login = client.post(
            "/api/v1/auth/login",
            json={"email": "updateself@example.com", "password": "Test1234!"},
        )
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.put(
            f"/api/v1/persons/{person_id}",
            json={"first_name": "Петр", "last_name": "Петров"},
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["first_name"] == "Петр"

    def test_change_password(self, client):
        """Смена пароля через API."""
        payload = {
            "first_name": "Иван",
            "last_name": "Иванов",
            "middle_name": "Иванович",
            "phone": "+79001234567",
            "passport": "PWD1234567",
            "email": "pwdself@example.com",
            "password": "Test1234!",
        }
        reg = client.post("/api/v1/auth/register", json=payload)
        assert reg.status_code == 200
        person_id = reg.json()["id"]

        login = client.post(
            "/api/v1/auth/login",
            json={"email": "pwdself@example.com", "password": "Test1234!"},
        )
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.put(
            f"/api/v1/persons/{person_id}/password",
            json={"old_password": "Test1234!", "new_password": "NewPass123!"},
            headers=headers,
        )
        assert response.status_code == 200

    def test_delete_person(self, client, admin_headers):
        """Удаление пользователя через API (только admin).

        Создаём через POST /persons/ (без роли), чтобы избежать
        конфликта внешних ключей при удалении.
        """
        payload = {
            "first_name": "Иван",
            "last_name": "Иванов",
            "middle_name": "Иванович",
            "phone": "+79001234567",
            "passport": "DEL1234567",
            "email": "delete@example.com",
            "password": "Test1234!",
        }
        create_response = client.post(
            "/api/v1/persons/", json=payload, headers=admin_headers
        )
        assert create_response.status_code == 201
        person_id = create_response.json()["id"]

        response = client.delete(
            f"/api/v1/persons/{person_id}", headers=admin_headers
        )
        assert response.status_code == 200
        assert response.json()["deleted_id"] == person_id