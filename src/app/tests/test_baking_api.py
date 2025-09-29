# src/app/tests/test_baking_api.py

import pytest
from fastapi.testclient import TestClient
from src.app.main import app
from src.app.database import get_db
from src.app.models import Transaction

# Création du client de test FastAPI
client = TestClient(app)

# ------------------------------
# Fixture pour réinitialiser la base avant chaque test
# ------------------------------
@pytest.fixture(autouse=True)
def reset_db_before_test():
    """
    Réinitialise la base de données avant chaque test et remet les comptes à zéro.
    """
    client.post("/reset")

    # Purge manuelle de la table Transaction (sécurise la DB)
    db = next(get_db())
    db.query(Transaction).delete()
    db.commit()

    yield

    client.post("/reset")

# ------------------------------
# Fixture pour récupérer un token JWT
# ------------------------------
@pytest.fixture
def auth_token():
    """
    Récupère un token valide pour les tests nécessitant authentification.
    Si tu utilises AppRole Vault, adapte ici la génération du token.
    """
    # Exemple : création d'un token de test ou login
    response = client.post("/login", json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200
    token = response.json().get("access_token")
    return token

# ------------------------------
# Tests unitaires sur les comptes et transactions
# ------------------------------

def test_create_account_with_initial_balance():
    response = client.post("/event", json={"type": "deposit", "destination": "100", "amount": 10})
    assert response.status_code == 201
    assert response.json() == {
        "destination": {"id": "100", "balance": 10},
        "origin": None,
        "type": "deposit"
    }

def test_deposit_into_existing_account():
    client.post("/event", json={"type": "deposit", "destination": "100", "amount": 10})
    response = client.post("/event", json={"type": "deposit", "destination": "100", "amount": 10})
    assert response.status_code == 201
    assert response.json() == {
        "destination": {"id": "100", "balance": 20},
        "origin": None,
        "type": "deposit"
    }

def test_get_balance_existing_account(auth_token):
    # Déposer de l'argent
    client.post("/event", json={"type": "deposit", "destination": "100", "amount": 20})

    # Commit explicite pour que la DB reflète les changements
    db = next(get_db())
    db.commit()

    # GET /balance avec authentification
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/balance", params={"account_id": "100"}, headers=headers)

    assert response.status_code == 200
    assert response.json() == {"account_id": "100", "balance": 20}

def test_withdraw_from_existing_account():
    client.post("/event", json={"type": "deposit", "destination": "100", "amount": 20})
    response = client.post("/event", json={"type": "withdraw", "origin": "100", "amount": 5})
    assert response.status_code == 201
    assert response.json() == {
        "origin": {"id": "100", "balance": 15},
        "destination": None,
        "type": "withdraw"
    }

def test_transfer_from_existing_account():
    client.post("/event", json={"type": "deposit", "destination": "100", "amount": 50})
    client.post("/event", json={"type": "deposit", "destination": "200", "amount": 10})
    response = client.post("/event", json={
        "type": "transfer",
        "origin": "100",
        "destination": "200",
        "amount": 20
    })
    assert response.status_code == 201
    assert response.json() == {
        "origin": {"id": "100", "balance": 30},
        "destination": {"id": "200", "balance": 30},
        "type": "transfer"
    }

