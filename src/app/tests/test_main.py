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

def test_protected(client):
    # Test endpoint /protected
    response = client.get("/protected")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data

def test_read_users_me(client):
    # Test endpoint /users/me
    response = client.get("/users/me")
    assert response.status_code == 200
    data = response.json()
    assert "user" in data

def test_create_user_form(client):
    # Test GET /create_user (formulaire HTML)
    response = client.get("/create_user")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_create_user_post_success(client):
    # Test POST /create_user (succès)
    response = client.post("/create_user", data={"email": "test@example.com", "password": "pass123"})
    assert response.status_code == 200
    data = response.json()
    assert "Utilisateur créé" in data["message"]
    assert "user_id" in data

def test_create_user_post_error(client):
    # Test POST /create_user (erreur, e.g., email dupliqué)
    # Simule une erreur en forçant un rollback
    response = client.post("/create_user", data={"email": "invalid", "password": ""})
    assert response.status_code == 400  # Erreur gérée

def test_create_account_endpoint(client, db):
    # Test POST /accounts/
    from schemas import AccountCreate
    account_data = AccountCreate(id="testacc", balance=100.0)
    response = client.post("/accounts/", json=account_data.dict())
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "testacc"

def test_get_balance_not_found(client):
    # Test GET /balance (compte inexistant)
    response = client.get("/balance", params={"account_id": "nonexistent"})
    assert response.status_code == 404
    data = response.json()
    assert "Account not found" in data["detail"]

def test_reset_state(client):
    # Test POST /reset
    response = client.post("/reset")
    assert response.status_code == 200
    data = response.json()
    assert "API reset executed" in data["message"]

def test_process_transaction_withdraw_insufficient_balance(client):
    # Test POST /event (retrait avec solde insuffisant)
    # D'abord déposer
    client.post("/event", json={"type": "deposit", "destination": "acc1", "amount": 50})
    # Puis retirer plus
    response = client.post("/event", json={"type": "withdraw", "origin": "acc1", "amount": 100})
    assert response.status_code == 403
    data = response.json()
    assert "Insufficient balance" in data["detail"]

def test_process_transaction_transfer_failed(client):
    # Test POST /event (transfert échoué)
    response = client.post("/event", json={"type": "transfer", "origin": "nonexistent", "destination": "acc1", "amount": 50})
    assert response.status_code == 404
    data = response.json()
    assert "Account not found" in data["detail"]

def test_github_webhook(client):
    # Test POST /github-webhook
    payload = {"action": "push", "repository": {"name": "test"}}
    response = client.post("/github-webhook/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "received"
