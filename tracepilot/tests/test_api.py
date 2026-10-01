from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_safety_rejection():
    response = client.post("/investigate", json={"query": "deploy the new version"})
    assert response.status_code == 400
    assert "Safety violation" in response.json()["detail"]
