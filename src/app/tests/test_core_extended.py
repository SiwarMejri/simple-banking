import pytest
from src.app.core import core
from src.app.models.account import Account

def test_create_or_update_account_new():
    core.reset_state()
    acc = core.create_or_update_account("acc1", 50)
    assert acc.id == "acc1"
    assert acc.balance == 50

def test_create_or_update_account_existing():
    core.reset_state()
    core.create_or_update_account("acc1", 50)
    acc = core.create_or_update_account("acc1", 25)
    assert acc.balance == 75

def test_withdraw_from_account_success():
    core.reset_state()
    core.create_or_update_account("acc1", 100)
    acc = core.withdraw_from_account("acc1", 50)
    assert acc.balance == 50

def test_withdraw_from_account_insufficient_balance():
    core.reset_state()
    core.create_or_update_account("acc1", 30)
    acc = core.withdraw_from_account("acc1", 50)
    assert acc is None

def test_transfer_between_accounts_success():
    core.reset_state()
    core.create_or_update_account("a1", 100)
    core.create_or_update_account("a2", 50)
    origin, dest = core.transfer_between_accounts("a1", "a2", 40)
    assert origin.balance == 60
    assert dest.balance == 90

def test_transfer_between_accounts_insufficient_balance():
    core.reset_state()
    core.create_or_update_account("a1", 30)
    core.create_or_update_account("a2", 50)
    origin, dest = core.transfer_between_accounts("a1", "a2", 40)
    assert origin is None and dest is None

def test_process_transaction_missing_params(db):
    result = core.process_transaction(db, {})
    assert result["status"] == "failed"

def test_process_transaction_non_existing_account(db):
    data = {"from_account": "unknown1", "to_account": "unknown2", "amount": 10}
    result = core.process_transaction(db, data)
    assert result["status"] == "failed"
