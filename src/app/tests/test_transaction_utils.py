import pytest
from src.app.models.transaction_utils import calculate_fee, validate_transaction, process_deposit, process_withdraw, process_transfer

def test_calculate_fee():
    assert calculate_fee(100) == 2.0
    assert calculate_fee(50) == 1.0

def test_validate_transaction_valid():
    assert validate_transaction(100, 50) is True

def test_validate_transaction_invalid_amount():
    with pytest.raises(ValueError, match="Montant invalide"):
        validate_transaction(100, -10)

def test_validate_transaction_insufficient_balance():
    with pytest.raises(ValueError, match="Solde insuffisant"):
        validate_transaction(50, 100)

def test_process_deposit():
    transaction = {"amount": 100, "destination": "acc1"}
    result = process_deposit(transaction)
    assert result["type"] == "deposit"
    assert result["destination"]["balance"] == 100

def test_process_withdraw():
    transaction = {"amount": 50, "origin": "acc1"}
    result = process_withdraw(transaction)
    assert result["type"] == "withdraw"
    assert result["origin"]["balance"] == 50

def test_process_transfer():
    transaction = {"amount": 50, "origin": "acc1", "destination": "acc2"}
    result = process_transfer(transaction)
    assert result["type"] == "transfer"
    assert result["origin"]["balance"] == 50
    assert result["destination"]["balance"] == 50
