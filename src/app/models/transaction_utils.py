# tests/test_transaction_utils.py

import pytest
from unittest.mock import patch, MagicMock
from fastapi import Response
from src.app.models.transaction_utils import (
    process_deposit,
    process_withdraw,
    process_transfer,
    INVALID_AMOUNT_MSG,
    INSUFFICIENT_BALANCE_MSG
)

# ------------------ Fixtures ------------------
@pytest.fixture
def mock_db_session():
    """Mock de SessionLocal pour éviter de toucher à la vraie DB"""
    with patch("src.app.models.transaction_utils.SessionLocal") as mock_session:
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        yield mock_db

@pytest.fixture
def response():
    return Response()

# ------------------ Tests process_deposit ------------------
def test_process_deposit_success(mock_db_session):
    transaction = {"destination": "A", "amount": 100}
    result = process_deposit(transaction)
    assert result["type"] == "deposit"
    assert result["destination"]["id"] == "A"
    assert result["destination"]["balance"] == 100

def test_process_deposit_invalid_amount(response):
    transaction = {"destination": "A", "amount": -10}
    result = process_deposit(transaction, response)
    assert response.status_code == 400
    assert result["error"] == INVALID_AMOUNT_MSG

# ------------------ Tests process_withdraw ------------------
def test_process_withdraw_success(mock_db_session):
    transaction = {"origin": "A", "amount": 50}
    # Simuler un solde de 100
    mock_db_session.query().filter_by().all.return_value = [
        MagicMock(type="deposit", amount=100)
    ]
    result = process_withdraw(transaction)
    assert result["type"] == "withdraw"
    assert result["origin"]["balance"] == 50

def test_process_withdraw_insufficient_balance(response, mock_db_session):
    transaction = {"origin": "A", "amount": 200}
    mock_db_session.query().filter_by().all.return_value = [
        MagicMock(type="deposit", amount=100)
    ]
    result = process_withdraw(transaction, response)
    assert response.status_code == 403
    assert result["error"] == INSUFFICIENT_BALANCE_MSG

def test_process_withdraw_invalid_amount(response):
    transaction = {"origin": "A", "amount": -5}
    result = process_withdraw(transaction, response)
    assert response.status_code == 400
    assert result["error"] == INVALID_AMOUNT_MSG

# ------------------ Tests process_transfer ------------------
def test_process_transfer_success(mock_db_session):
    transaction = {"origin": "A", "destination": "B", "amount": 50}

    # Fonction pour simuler différents soldes selon l'utilisateur
    def query_side_effect(*args, **kwargs):
        if kwargs.get("destination") == "A":
            return [MagicMock(type="deposit", amount=100)]
        return []

    mock_db_session.query().filter_by().all.side_effect = query_side_effect
    result = process_transfer(transaction)
    assert result["type"] == "transfer"
    assert result["origin"]["balance"] == 50
    assert result["destination"]["balance"] == 50

def test_process_transfer_insufficient_balance(response, mock_db_session):
    transaction = {"origin": "A", "destination": "B", "amount": 200}
    mock_db_session.query().filter_by().all.return_value = [
        MagicMock(type="deposit", amount=100)
    ]
    result = process_transfer(transaction, response)
    assert response.status_code == 403
    assert result["error"] == INSUFFICIENT_BALANCE_MSG

def test_process_transfer_invalid_amount(response):
    transaction = {"origin": "A", "destination": "B", "amount": -10}
    result = process_transfer(transaction, response)
    assert response.status_code == 400
    assert result["error"] == INVALID_AMOUNT_MSG
