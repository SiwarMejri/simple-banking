import sys
import os
import pytest
from starlette.testclient import TestClient

# Ajoute src/ au path pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.app.main import app
from src.app.models.base import Base
from src.app.models.database import engine
from src.app.core import core

# Les tests utilisent la fixture client de conftest.py

def test_create_account_with_initial_balance(client):
    # CORRECTION : utiliser account_id au lieu de destination
    response = client.post("/event", json={"type": "deposit", "account_id": "100", "amount": 10})
    assert response.status_code == 200, f"Erreur: {response.text}"
    body = response.json()
    # Vérifications flexibles
    assert body.get("type") == "deposit"
    assert "account_id" in body and body["account_id"] == "100"

def test_get_balance_existing_account(client):
    # Ajouter un reset pour isoler le test
    client.post("/reset")
    
    # CORRECTION : utiliser account_id au lieu de destination
    client.post("/event", json={"type": "deposit", "account_id": "100", "amount": 20})
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
