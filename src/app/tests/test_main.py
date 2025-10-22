# tests/test_main.py
import sys
import os
from fastapi.testclient import TestClient

# Ajoute src/ au path pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app.main import app

# Supprimez le client global et utilisez la fixture de conftest.py pour cohérence
# client = TestClient(app)  # Supprimé

def test_root(client):  # Utilise la fixture client
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data or "Hello" in response.text

def test_event_deposit(client):
    payload = {"type": "deposit", "destination": "acc1", "amount": 100}
    response = client.post("/event", json=payload)
    assert response.status_code in (200, 201), f"Erreur: {response.text}"
    body = response.json()
    assert "destination" in body

def test_event_invalid_request(client):
    payload = {"type": "invalid_type", "amount": 0}
    response = client.post("/event", json=payload)
    assert response.status_code in (400, 422), f"Erreur: {response.status_code}"
