import pytest
from app.runtime.app import create_app
from app.runtime.config import RuntimeSettings
from fastapi.testclient import TestClient


@pytest.fixture
def test_app():
    return create_app(RuntimeSettings(database_url="sqlite+aiosqlite:///:memory:", environment="test"))


@pytest.fixture
def test_client(test_app):
    with TestClient(test_app) as client:
        yield client


@pytest.fixture
def register(test_client):
    def create(email="learner@example.com", tenant_type="individual"):
        response = test_client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "Secure-pass-12345",
                "name": "Test Learner",
                "tenant_type": tenant_type,
                "consent": True,
            },
        )
        assert response.status_code == 201, response.text
        data = response.json()
        return {"Authorization": f"Bearer {data['access_token']}"}, data

    return create
