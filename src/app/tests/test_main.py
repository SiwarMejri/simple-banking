# tests/test_main.py
import pytest
from fastapi.testclient import TestClient
from src.app.main import app
from src.app.schemas import Account as AccountSchema

client = TestClient(app)


# ---------------- Test de la racine ----------------
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Simple Banking API!"}


# ---------------- Test de create_user ----------------
def test_create_user_form():
    response = client.get("/create_user")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_create_user_post():
    response = client.post("/create_user", data={"email": "alice@test.com", "password": "1234"})
    assert response.status_code == 200
    json_data = response.json()
    assert "user_id" in json_data
    assert json_data["email"] == "alice@test.com"


# ---------------- Test de accounts ----------------
def test_create_account():
    payload = {"id": "acc_test", "user_id": 1}
    response = client.post("/accounts/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "acc_test"
    assert data["balance"] == 0


# ---------------- Test de balance ----------------
def test_get_balance_existing():
    # Crée d'abord un compte en mémoire
    client.post("/event", json={"type": "deposit", "destination": "acc_balance", "amount": 100})
    response = client.get("/balance", params={"account_id": "acc_balance"})
    assert response.status_code == 200
    data = response.json()
    assert data["account_id"] == "acc_balance"
    assert data["balance"] == 100

def test_get_balance_not_found():
    response = client.get("/balance", params={"account_id": "nonexistent"})
    assert response.status_code == 404


# ---------------- Test de reset ----------------
def test_reset_state():
    response = client.post("/reset")
    assert response.status_code == 200
    assert "API reset executed" in response.json()["message"]


# ---------------- Test de event (transactions) ----------------
def test_event_deposit():
    payload = {"type": "deposit", "destination": "acc1", "amount": 100}
    response = client.post("/event", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "deposit"
    assert data["destination"]["balance"] == 100

def test_event_withdraw():
    # Préparer le compte
    client.post("/event", json={"type": "deposit", "destination": "acc2", "amount": 200})
    payload = {"type": "withdraw", "origin": "acc2", "amount": 50}
    response = client.post("/event", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "withdraw"
    assert data["origin"]["balance"] == 150

def test_event_transfer():
    # Préparer les comptes
    client.post("/event", json={"type": "deposit", "destination": "acc3", "amount": 100})
    client.post("/event", json={"type": "deposit", "destination": "acc4", "amount": 50})
    payload = {"type": "transfer", "origin": "acc3", "destination": "acc4", "amount": 40}
    response = client.post("/event", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "transfer"
    assert data["origin"]["balance"] == 60
    assert data["destination"]["balance"] == 90

def test_event_invalid_type():
    payload = {"type": "invalid_type", "amount": 10}
    response = client.post("/event", json=payload)
    assert response.status_code == 400


# ---------------- Test GitHub webhook ----------------
def test_github_webhook():
    payload = {"ref": "refs/heads/main", "repository": {"name": "test_repo"}}
    response = client.post("/github-webhook/", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "received"
