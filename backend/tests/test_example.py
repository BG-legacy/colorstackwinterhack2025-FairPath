"""
Example tests - using pytest
Add more tests as you build features
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    """Testing the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_health_endpoint():
    """Testing health check"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_example_endpoint():
    """Testing example endpoint"""
    response = client.get("/api/example/test")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "data" in data

def test_example_post_validation():
    """Testing request validation"""
    # should fail without required field
    response = client.post("/api/example/process", json={})
    assert response.status_code == 422  # validation error
    
    # should work with valid data
    response = client.post("/api/example/process", json={
        "text": "test input",
        "count": 5
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "data" in data









