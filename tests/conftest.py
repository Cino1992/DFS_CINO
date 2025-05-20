import pytest
from fastapi.testclient import TestClient
from app import app
import mongomock
import os
from unittest.mock import patch
from app.db.mongo_client import MongoDB


# Override MongoDB client with mongomock for testing
@pytest.fixture(autouse=True)
def mock_mongodb():
    with patch.object(MongoDB, "connect") as mock_connect:
        # Set up mock MongoDB client
        MongoDB.client = mongomock.MongoClient()
        MongoDB.db = MongoDB.client["test_db"]
        yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_user():
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123"
    }


@pytest.fixture
def test_token(client, test_user):
    # Register a test user
    client.post("/api/v1/users", json=test_user)

    # Get token
    response = client.post(
        "/api/v1/token",
        data={"username": test_user["username"], "password": test_user["password"]}
    )

    token = response.json()["access_token"]
    return token


@pytest.fixture
def auth_headers(test_token):
    return {"Authorization": f"Bearer {test_token}"}