# tests/test_transaction_utils.py
import pytest
from src.app.models import transaction_utils as tu

def test_calculate_fee():
    assert tu.calculate_fee(100) == 2
    assert tu.calculate_fee(0) == 0
    assert tu.calculate_fee(1000) == 20

def test_validate_transaction_valid():
    assert tu.validate_transaction(200, 100) is True

def test_validate_transaction_invalid_amount():
    with pytest.raises(ValueError, match="Montant invalide"):
        tu.validate_transaction(-10, 100)

def test_validate_transaction_insufficient_balance():
    with pytest.raises(ValueError, match="Solde insuffisant"):
        tu.validate_transaction(300, 200)

def test_process_deposit():
    tx = {"destination": "acc1", "amount": 100}
    result = tu.process_deposit(tx)
    assert result["type"] == "deposit"
    assert "destination" in result

def test_process_withdraw():
    tx = {"origin": "acc1", "amount": 50}
    result = tu.process_withdraw(tx)
    assert result["type"] == "withdraw"
    assert "origin" in result

def test_process_transfer():
    tx = {"origin": "a1", "destination": "a2", "amount": 40}
    result = tu.process_transfer(tx)
    assert result["type"] == "transfer"
    assert "origin" in result
    assert "destination" in result
