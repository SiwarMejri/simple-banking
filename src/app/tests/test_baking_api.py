import os
import pytest
from starlette.testclient import TestClient
from src.app.main import app
from src.app.database import Base, engine
from src.app.core import core

# ---------------- Fixture pour réinitialiser la DB avant et après chaque test ----------------
@pytest.fixture(autouse=True)
def reset_db():
    os.environ["TESTING"] = "1"
    try:
        # Reset complet de la DB et de l'état core
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        core.reset_state()
        yield
    finally:
        Base.metadata.drop_all(bind=engine)
        core.reset_state()
        os.environ.pop("TESTING", None)

# ---------------- Fixture client ----------------
@pytest.fixture
def client():
    # Reset API state avant chaque test pour être sûr
    client_instance = TestClient(app)
    client_instance.post("/reset")
    return client_instance

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
