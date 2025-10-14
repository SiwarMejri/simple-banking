# src/app/tests/test_baking_api.py

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core import core  # ✅ importer core depuis app.core
# On utilise core.reset_state() (et non directement reset_state)

client = TestClient(app)

# ------------------ Fixtures ------------------
@pytest.fixture(autouse=True)
def reset_db_before_test():
    """Réinitialise l'état avant et après chaque test"""
    core.reset_state()
    yield
    core.reset_state()

@pytest.fixture
def auth_token():
    """Token factice pour bypass JWT en mode test"""
    return "any-token"

# ------------------ Tests ------------------
def test_create_account_with_initial_balance():
    response = client.post("/event", json={"type": "deposit", "destination": "100", "amount": 10})
    assert response.status_code == 200
    assert response.json() == {
        "destination": {"id": "100", "balance": 10},
        "origin": None,
        "type": "deposit"
    }

def test_deposit_into_existing_account():
    client.post("/event", json={"type": "deposit", "destination": "100", "amount": 10})
    response = client.post("/event", json={"type": "deposit", "destination": "100", "amount": 10})
    assert response.status_code == 200
    assert response.json() == {
        "destination": {"id": "100", "balance": 20},
        "origin": None,
        "type": "deposit"
    }

def test_get_balance_existing_account(auth_token):
    client.post("/event", json={"type": "deposit", "destination": "100", "amount": 20})
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/balance", params={"account_id": "100"}, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"account_id": "100", "balance": 20}

def test_withdraw_from_existing_account():
    client.post("/event", json={"type": "deposit", "destination": "100", "amount": 20})
    response = client.post("/event", json={"type": "withdraw", "origin": "100", "amount": 5})
    assert response.status_code == 200
    assert response.json() == {
        "origin": {"id": "100", "balance": 15},
        "destination": None,
        "type": "withdraw"
    }

def test_transfer_from_existing_account():
    client.post("/event", json={"type": "deposit", "destination": "100", "amount": 50})
    client.post("/event", json={"type": "deposit", "destination": "200", "amount": 10})
    response = client.post("/event", json={"type": "transfer", "origin": "100", "destination": "200", "amount": 20})
    assert response.status_code == 200
    assert response.json() == {
        "origin": {"id": "100", "balance": 30},
        "destination": {"id": "200", "balance": 30},
        "type": "transfer"
    }
