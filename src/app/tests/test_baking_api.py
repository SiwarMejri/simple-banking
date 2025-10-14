# src/app/tests/test_banking_api.py
import pytest
from starlette.testclient import TestClient
from src.app.main import app
from src.app.database import Base, engine

# ------------------ Fixtures ------------------

@pytest.fixture(autouse=True)
def reset_db():
    """Reset la DB avant chaque test pour éviter l'accumulation."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    """Client TestClient pour interagir avec l'API FastAPI."""
    return TestClient(app)

# ------------------ Tests ------------------

def test_create_account_with_initial_balance(client):
    response = client.post("/event", json={"type": "deposit", "destination": "100", "amount": 10})
    assert response.status_code == 200
    assert response.json() == {
        "destination": {"id": "100", "balance": 10},
        "origin": None,
        "type": "deposit"
    }

def test_deposit_into_existing_account(client):
    client.post("/event", json={"type": "deposit", "destination": "100", "amount": 10})
    response = client.post("/event", json={"type": "deposit", "destination": "100", "amount": 10})
    assert response.status_code == 200
    assert response.json() == {
        "destination": {"id": "100", "balance": 20},
        "origin": None,
        "type": "deposit"
    }

def test_get_balance_existing_account(client):
    client.post("/event", json={"type": "deposit", "destination": "100", "amount": 20})
    response = client.get("/balance", params={"account_id": "100"})
    assert response.status_code == 200
    assert response.json() == {"account_id": "100", "balance": 20}

def test_withdraw_from_existing_account(client):
    client.post("/event", json={"type": "deposit", "destination": "100", "amount": 20})
    response = client.post("/event", json={"type": "withdraw", "origin": "100", "amount": 5})
    assert response.status_code == 200
    assert response.json() == {
        "origin": {"id": "100", "balance": 15},
        "destination": None,
        "type": "withdraw"
    }

def test_transfer_from_existing_account(client):
    client.post("/event", json={"type": "deposit", "destination": "100", "amount": 50})
    client.post("/event", json={"type": "deposit", "destination": "200", "amount": 10})
    response = client.post("/event", json={"type": "transfer", "origin": "100", "destination": "200", "amount": 20})
    assert response.status_code == 200
    assert response.json() == {
        "origin": {"id": "100", "balance": 30},
        "destination": {"id": "200", "balance": 30},
        "type": "transfer"
    }
