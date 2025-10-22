import os
import pytest
from starlette.testclient import TestClient
from src.app.main import app
from src.app.database import Base, engine
from src.app.core import core

# ---------------- Tests ----------------
def test_create_account_with_initial_balance(client):
    response = client.post("/event", json={"type": "deposit", "destination": "100", "amount": 10})
    assert response.status_code == 200
    assert response.json() == {
        "destination": {"id": "100", "balance": 10},
        "origin": None,
        "type": "deposit"
    }

def test_get_balance_existing_account(client):
    # Création d'un dépôt pour avoir un solde propre
    client.post("/event", json={"type": "deposit", "destination": "100", "amount": 20})
    response = client.get("/balance", params={"account_id": "100"})
    assert response.status_code == 200
    assert response.json() == {"account_id": "100", "balance": 20}

def test_reset_api_state(client):
    response = client.post("/reset")
    assert response.status_code == 200
    assert response.json() == {"message": "API reset executed"}
