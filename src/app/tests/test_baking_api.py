import requests

BASE_URL = "http://localhost:8000"

def reset_state():
    requests.post(f"{BASE_URL}/reset")

# ------------------------------
# Tests sur les comptes existants
# ------------------------------

def test_create_account_with_initial_balance():
    reset_state()
    response = requests.post(f"{BASE_URL}/event", json={"type": "deposit", "destination": "100", "amount": 10})
    assert response.status_code == 201
    assert response.json() == {
        "destination": {"id": "100", "balance": 10},
        "origin": None,
        "type": "deposit"
    }

def test_deposit_into_existing_account():
    reset_state()
    requests.post(f"{BASE_URL}/event", json={"type": "deposit", "destination": "100", "amount": 10})
    response = requests.post(f"{BASE_URL}/event", json={"type": "deposit", "destination": "100", "amount": 10})
    assert response.status_code == 201
    assert response.json() == {
        "destination": {"id": "100", "balance": 20},
        "origin": None,
        "type": "deposit"
    }

def test_get_balance_existing_account():
    reset_state()
    requests.post(f"{BASE_URL}/event", json={"type": "deposit", "destination": "100", "amount": 20})
    response = requests.get(f"{BASE_URL}/balance?account_id=100")
    assert response.status_code == 200
    assert response.json() == {"account_id": "100", "balance": 20}

def test_withdraw_from_existing_account():
    reset_state()
    requests.post(f"{BASE_URL}/event", json={"type": "deposit", "destination": "100", "amount": 20})
    response = requests.post(f"{BASE_URL}/event", json={"type": "withdraw", "origin": "100", "amount": 5})
    assert response.status_code == 201
    assert response.json() == {
        "origin": {"id": "100", "balance": 15},
        "destination": None,
        "type": "withdraw"
    }

def test_transfer_from_existing_account():
    reset_state()
    requests.post(f"{BASE_URL}/event", json={"type": "deposit", "destination": "100", "amount": 50})
    requests.post(f"{BASE_URL}/event", json={"type": "deposit", "destination": "200", "amount": 10})
    response = requests.post(f"{BASE_URL}/event", json={"type": "transfer", "origin": "100", "destination": "200", "amount": 20})
    assert response.status_code == 201
    assert response.json() == {
        "origin": {"id": "100", "balance": 30},
        "destination": {"id": "200", "balance": 30},
        "type": "transfer"
    }

