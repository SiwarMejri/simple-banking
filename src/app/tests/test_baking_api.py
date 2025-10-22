import sys
import os
import pytest
from starlette.testclient import TestClient

# Ajoute src/ au path pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app.main import app
from app.models.base import Base
from app.models.database import engine
from app.core import core

# Les tests utilisent la fixture client de conftest.py

def test_create_account_with_initial_balance(client):
    response = client.post("/event", json={"type": "deposit", "destination": "100", "amount": 10})
    assert response.status_code == 200, f"Erreur: {response.text}"
    body = response.json()
    # Vérifications flexibles
    assert body.get("type") == "deposit"
    assert "destination" in body and body["destination"]["id"] == "100"
    assert body["destination"]["balance"] == 10

def test_get_balance_existing_account(client):
    # Ajouter un reset pour isoler le test
    client.post("/reset")
    
    client.post("/event", json={"type": "deposit", "destination": "100", "amount": 20})
    response = client.get("/balance", params={"account_id": "100"})
    assert response.status_code == 200, f"Erreur: {response.text}"
    body = response.json()
    assert body.get("account_id") == "100"
    assert body.get("balance") == 20

def test_reset_api_state(client):
    response = client.post("/reset")
    assert response.status_code == 200, f"Erreur: {response.text}"
    body = response.json()
    assert body.get("message") == "API reset executed"
