import pytest
from src.app.models import transaction_utils as tu


class DummyResponse:
    def __init__(self):
        self.status_code = None


def test_process_deposit_invalid_amount_sets_response():
    tx = {"destination": "acc1", "amount": -50}
    resp = DummyResponse()
    result = tu.process_deposit(tx, resp)
    assert "error" in result
    assert resp.status_code == 400


def test_process_withdraw_invalid_amount_sets_response():
    tx = {"origin": "acc1", "amount": -5}
    resp = DummyResponse()
    result = tu.process_withdraw(tx, resp)
    assert result["error"] == tu.INVALID_AMOUNT_MSG
    assert resp.status_code == 400


def test_process_withdraw_insufficient_balance_sets_response():
    tx = {"origin": "acc1", "amount": 200}
    resp = DummyResponse()
    result = tu.process_withdraw(tx, resp)
    assert result["error"] == tu.INSUFFICIENT_BALANCE_MSG
    assert resp.status_code == 403


def test_process_transfer_invalid_amount_sets_response():
    tx = {"origin": "a1", "destination": "a2", "amount": 0}
    resp = DummyResponse()
    result = tu.process_transfer(tx, resp)
    assert result["error"] == tu.INVALID_AMOUNT_MSG
    assert resp.status_code == 400


def test_process_transfer_insufficient_balance_sets_response():
    tx = {"origin": "a1", "destination": "a2", "amount": 500}
    resp = DummyResponse()
    result = tu.process_transfer(tx, resp)
    assert result["error"] == tu.INSUFFICIENT_BALANCE_MSG
    assert resp.status_code == 403
