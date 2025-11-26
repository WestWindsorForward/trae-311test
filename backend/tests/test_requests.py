import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

class TestRequests:
    def test_create_request_success(self, client: TestClient, test_user_data: dict, test_request_data: dict):
        """Test creating a service request."""
        # Register and login
        client.post("/api/auth/register", json=test_user_data)
        login_response = client.post("/api/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        })
        token = login_response.json()["access_token"]
        
        # Create request
        response = client.post("/api/requests", json=test_request_data, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == test_request_data["title"]
        assert data["description"] == test_request_data["description"]
        assert data["category"] == test_request_data["category"]
        assert data["status"] == "submitted"
        assert "id" in data

    def test_create_request_no_auth(self, client: TestClient, test_request_data: dict):
        """Test creating a request without authentication."""
        response = client.post("/api/requests", json=test_request_data)
        assert response.status_code == 401

    def test_get_requests_list(self, client: TestClient, test_user_data: dict, test_request_data: dict):
        """Test getting list of requests."""
        # Register and login
        client.post("/api/auth/register", json=test_user_data)
        login_response = client.post("/api/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        })
        token = login_response.json()["access_token"]
        
        # Create a request
        client.post("/api/requests", json=test_request_data, headers={"Authorization": f"Bearer {token}"})
        
        # Get requests list
        response = client.get("/api/requests", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 1

    def test_get_request_detail(self, client: TestClient, test_user_data: dict, test_request_data: dict):
        """Test getting request details."""
        # Register and login
        client.post("/api/auth/register", json=test_user_data)
        login_response = client.post("/api/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        })
        token = login_response.json()["access_token"]
        
        # Create a request
        create_response = client.post("/api/requests", json=test_request_data, headers={"Authorization": f"Bearer {token}"})
        request_id = create_response.json()["id"]
        
        # Get request detail
        response = client.get(f"/api/requests/{request_id}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == request_id
        assert data["title"] == test_request_data["title"]

    def test_get_request_not_found(self, client: TestClient, test_user_data: dict):
        """Test getting non-existent request."""
        # Register and login
        client.post("/api/auth/register", json=test_user_data)
        login_response = client.post("/api/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        })
        token = login_response.json()["access_token"]
        
        # Get non-existent request
        response = client.get("/api/requests/999", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404

    def test_filter_requests_by_status(self, client: TestClient, test_user_data: dict, test_request_data: dict):
        """Test filtering requests by status."""
        # Register and login
        client.post("/api/auth/register", json=test_user_data)
        login_response = client.post("/api/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        })
        token = login_response.json()["access_token"]
        
        # Create a request
        client.post("/api/requests", json=test_request_data, headers={"Authorization": f"Bearer {token}"})
        
        # Filter by status
        response = client.get("/api/requests?status=submitted", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        assert all(item["status"] == "submitted" for item in data["items"])

    def test_search_requests(self, client: TestClient, test_user_data: dict, test_request_data: dict):
        """Test searching requests."""
        # Register and login
        client.post("/api/auth/register", json=test_user_data)
        login_response = client.post("/api/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        })
        token = login_response.json()["access_token"]
        
        # Create a request
        client.post("/api/requests", json=test_request_data, headers={"Authorization": f"Bearer {token}"})
        
        # Search requests
        response = client.get(f"/api/requests?search={test_request_data['title']}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1