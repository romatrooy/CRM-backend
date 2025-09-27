"""
Тесты для контактов
"""
import pytest
from fastapi.testclient import TestClient
from app.core.security import create_access_token


class TestContacts:
    """Тесты для работы с контактами"""
    
    def test_create_contact(self, client: TestClient, test_user):
        """Тест создания контакта"""
        # Получение токена
        token = create_access_token({"sub": str(test_user.id), "username": test_user.username})
        headers = {"Authorization": f"Bearer {token}"}
        
        contact_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "+1234567890",
            "status": "lead"
        }
        
        response = client.post("/api/v1/contacts/", json=contact_data, headers=headers)
        assert response.status_code == 201
        
        data = response.json()
        assert data["first_name"] == contact_data["first_name"]
        assert data["last_name"] == contact_data["last_name"]
        assert data["email"] == contact_data["email"]
        assert data["phone"] == contact_data["phone"]
        assert data["status"] == contact_data["status"]
        assert data["owner_id"] == test_user.id
    
    def test_get_contacts(self, client: TestClient, test_user):
        """Тест получения списка контактов"""
        token = create_access_token({"sub": str(test_user.id), "username": test_user.username})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/v1/contacts/", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "pages" in data
    
    def test_get_contact_by_id(self, client: TestClient, test_user, db_session):
        """Тест получения контакта по ID"""
        from app.models.contact import Contact
        
        # Создание тестового контакта
        contact = Contact(
            first_name="Test",
            last_name="Contact",
            email="test.contact@example.com",
            owner_id=test_user.id
        )
        db_session.add(contact)
        await db_session.commit()
        await db_session.refresh(contact)
        
        token = create_access_token({"sub": str(test_user.id), "username": test_user.username})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get(f"/api/v1/contacts/{contact.id}", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == contact.id
        assert data["first_name"] == contact.first_name
        assert data["last_name"] == contact.last_name
    
    def test_update_contact(self, client: TestClient, test_user, db_session):
        """Тест обновления контакта"""
        from app.models.contact import Contact
        
        # Создание тестового контакта
        contact = Contact(
            first_name="Test",
            last_name="Contact",
            email="test.contact@example.com",
            owner_id=test_user.id
        )
        db_session.add(contact)
        await db_session.commit()
        await db_session.refresh(contact)
        
        token = create_access_token({"sub": str(test_user.id), "username": test_user.username})
        headers = {"Authorization": f"Bearer {token}"}
        
        update_data = {
            "first_name": "Updated",
            "last_name": "Contact",
            "phone": "+1234567890"
        }
        
        response = client.put(f"/api/v1/contacts/{contact.id}", json=update_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["first_name"] == update_data["first_name"]
        assert data["phone"] == update_data["phone"]
    
    def test_delete_contact(self, client: TestClient, test_user, db_session):
        """Тест удаления контакта"""
        from app.models.contact import Contact
        
        # Создание тестового контакта
        contact = Contact(
            first_name="Test",
            last_name="Contact",
            email="test.contact@example.com",
            owner_id=test_user.id
        )
        db_session.add(contact)
        await db_session.commit()
        await db_session.refresh(contact)
        
        token = create_access_token({"sub": str(test_user.id), "username": test_user.username})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.delete(f"/api/v1/contacts/{contact.id}", headers=headers)
        assert response.status_code == 204
