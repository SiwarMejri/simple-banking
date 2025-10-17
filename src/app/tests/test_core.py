import pytest
from src.app.core.core import (
    reset_state,
    get_account_balance,
    create_or_update_account,
    withdraw_from_account,
    transfer_between_accounts,
    accounts
)

@pytest.fixture(autouse=True)
def clear_accounts():
    accounts.clear()
    yield
    accounts.clear()

def test_create_and_get_account():
    acc = create_or_update_account("A", 100)
    assert acc.balance == 100
    assert get_account_balance("A").balance == 100

def test_update_existing_account():
    create_or_update_account("A", 100)
    acc = create_or_update_account("A", 50)
    assert acc.balance == 150

def test_withdraw_success():
    create_or_update_account("A", 100)
    acc = withdraw_from_account("A", 50)
    assert acc.balance == 50

def test_withdraw_insufficient_balance():
    create_or_update_account("A", 100)
    assert withdraw_from_account("A", 200) is None

def test_transfer_success():
    create_or_update_account("A", 100)
    create_or_update_account("B", 50)
    origin, dest = transfer_between_accounts("A", "B", 50)
    assert origin.balance == 50
    assert dest.balance == 100

def test_transfer_insufficient_balance():
    create_or_update_account("A", 100)
    create_or_update_account("B", 50)
    origin, dest = transfer_between_accounts("A", "B", 200)
    assert origin is None and dest is None

def test_reset_state():
    create_or_update_account("A", 100)
    reset_state()
    assert len(accounts) == 0
