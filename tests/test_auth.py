"""
Тесты для аутентификации
"""
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


class TestAuth:
    """Тесты аутентификации"""
    
    def test_register_user(self, client: TestClient):
        """Тест регистрации пользователя"""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "full_name": "New User",
            "password": "newpassword123"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert data["full_name"] == user_data["full_name"]
        assert "id" in data
    
    def test_register_duplicate_email(self, client: TestClient, test_user):
        """Тест регистрации с дублирующимся email"""
        user_data = {
            "email": test_user.email,
            "username": "differentuser",
            "full_name": "Different User",
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 400
        assert "уже существует" in response.json()["detail"]
    
    def test_login_success(self, client: TestClient, test_user):
        """Тест успешного входа"""
        login_data = {
            "username": test_user.email,
            "password": "testpassword"
        }
        
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client: TestClient):
        """Тест входа с неверными данными"""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 401
        assert "Неверный email или пароль" in response.json()["detail"]
    
    def test_login_inactive_user(self, client: TestClient, db_session):
        """Тест входа неактивного пользователя"""
        from app.models.user import User
        from app.core.security import get_password_hash
        
        inactive_user = User(
            email="inactive@example.com",
            username="inactive",
            full_name="Inactive User",
            hashed_password=get_password_hash("password123"),
            is_active=False
        )
        
        db_session.add(inactive_user)
        await db_session.commit()
        
        login_data = {
            "username": inactive_user.email,
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 400
        assert "деактивирован" in response.json()["detail"]
