# tests/test_main.py
from fastapi.testclient import TestClient
from src.app.main import app

client = TestClient(app)

def test_root():
    """
    Vérifie que l'API FastAPI démarre correctement et répond sur la route /
    """
    response = client.get("/")
    assert response.status_code == 200
def test_event_deposit():
    payload = {"type": "deposit", "destination": "acc1", "amount": 100}
    response = client.post("/event", json=payload)
    assert response.status_code in (200, 201)
    assert "destination" in response.json()

def test_event_invalid_request():
    payload = {"type": "invalid_type", "amount": 0}
    response = client.post("/event", json=payload)
    assert response.status_code in (400, 422)
