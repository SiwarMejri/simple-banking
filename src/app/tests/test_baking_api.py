# tests/test_banking_api.py
import os
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core import core
from app.models.base import Base
from app.models.database import engine

# Active le mode test
os.environ["TESTING"] = "1"

client = TestClient(app)

# ------------------ Fixtures ------------------
@pytest.fixture(autouse=True)
def reset_db_before_test():
    """Réinitialise la base avant et après chaque test"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    core.reset_state()
    yield
    Base.metadata.drop_all(bind=engine)
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
    response = client.get("/balance", params={"account_id": "100"})
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
