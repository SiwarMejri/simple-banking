import pytest
from src.app.models import transaction_utils as tu

def test_validate_transaction_zero_amount():
    with pytest.raises(ValueError, match="Montant invalide"):
        tu.validate_transaction(100, 0)

def test_process_deposit_negative_amount():
    tx = {"destination": "acc1", "amount": -10}
    result = tu.process_deposit(tx)
    assert "error" in result and result["error"] == tu.INVALID_AMOUNT_MSG

def test_process_withdraw_insufficient_balance():
    tx = {"origin": "acc1", "amount": 200}  # balance simulée 100
    result = tu.process_withdraw(tx)
    assert "error" in result and result["error"] == tu.INSUFFICIENT_BALANCE_MSG

def test_process_transfer_invalid_amount():
    tx = {"origin": "a1", "destination": "a2", "amount": 0}
    result = tu.process_transfer(tx)
    assert "error" in result and result["error"] == tu.INVALID_AMOUNT_MSG
