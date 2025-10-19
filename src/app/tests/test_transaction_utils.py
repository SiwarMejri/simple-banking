# tests/test_transaction_utils.py
import pytest
from src.app.models.transaction_utils import calculate_fee, validate_transaction
from src.app.models import transaction_utils as tu

def test_calculate_fee():
    assert calculate_fee(100) == 2  # si fee = 2%
    assert calculate_fee(0) == 0
    assert calculate_fee(1000) == 20

def test_validate_transaction():
    assert validate_transaction({"amount": 100, "balance": 200}) is True
    assert validate_transaction({"amount": 300, "balance": 200}) is False
    with pytest.raises(ValueError):
        validate_transaction({"amount": -50, "balance": 200})
def test_validate_transaction_valid():
    assert tu.validate_transaction(200, 100) is True

def test_validate_transaction_invalid_amount():
    with pytest.raises(ValueError, match="Montant invalide"):
        tu.validate_transaction(200, 0)

def test_validate_transaction_insufficient_balance():
    with pytest.raises(ValueError, match="Solde insuffisant"):
        tu.validate_transaction(50, 100)

def test_process_deposit_valid():
    transaction = {"destination": "acc1", "amount": 100}
    result = tu.process_deposit(transaction)
    assert result["type"] == "deposit"
    assert result["destination"]["balance"] == 100

def test_process_deposit_invalid_amount():
    class Resp: pass
    resp = Resp()
    transaction = {"destination": "acc1", "amount": 0}
    result = tu.process_deposit(transaction, resp)
    assert result["error"] == tu.INVALID_AMOUNT_MSG
    assert resp.status_code == 400

def test_process_withdraw_valid():
    transaction = {"origin": "acc1", "amount": 50}
    result = tu.process_withdraw(transaction)
    assert result["type"] == "withdraw"
    assert result["origin"]["balance"] == 50

def test_process_withdraw_invalid_amount():
    class Resp: pass
    resp = Resp()
    transaction = {"origin": "acc1", "amount": -10}
    result = tu.process_withdraw(transaction, resp)
    assert result["error"] == tu.INVALID_AMOUNT_MSG
    assert resp.status_code == 400

def test_process_withdraw_insufficient_balance():
    class Resp: pass
    resp = Resp()
    transaction = {"origin": "acc1", "amount": 200}
    result = tu.process_withdraw(transaction, resp)
    assert result["error"] == tu.INSUFFICIENT_BALANCE_MSG
    assert resp.status_code == 403

def test_process_transfer_valid():
    transaction = {"origin": "a1", "destination": "a2", "amount": 40}
    result = tu.process_transfer(transaction)
    assert result["type"] == "transfer"
    assert result["origin"]["balance"] == 60
    assert result["destination"]["balance"] == 40

def test_process_transfer_invalid_amount():
    class Resp: pass
    resp = Resp()
    transaction = {"origin": "a1", "destination": "a2", "amount": 0}
    result = tu.process_transfer(transaction, resp)
    assert result["error"] == tu.INVALID_AMOUNT_MSG
    assert resp.status_code == 400

def test_process_transfer_insufficient_balance():
    class Resp: pass
    resp = Resp()
    transaction = {"origin": "a1", "destination": "a2", "amount": 200}
    result = tu.process_transfer(transaction, resp)
    assert result["error"] == tu.INSUFFICIENT_BALANCE_MSG
    assert resp.status_code == 403
