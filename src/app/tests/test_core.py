import pytest
from src.app.core import core
from src.app.models.account import AccountModel

@pytest.fixture
def setup_accounts():
    """Initialise deux comptes en mémoire avant chaque test."""
    core.accounts.clear()
    core.accounts["a1"] = AccountModel(id="a1", balance=100)
    core.accounts["a2"] = AccountModel(id="a2", balance=50)
    yield
    core.accounts.clear()

def test_create_account_and_balance():
    core.accounts.clear()
    core.accounts["u1"] = AccountModel(id="u1", balance=200)
    assert core.accounts["u1"].balance == 200

def test_update_account_balance():
    core.accounts.clear()
    core.accounts["u1"] = AccountModel(id="u1", balance=100)
    core.accounts["u1"].balance += 50
    assert core.accounts["u1"].balance == 150

def test_withdraw_success(setup_accounts):
    result = core.withdraw_from_account("a1", 50)
    assert result.balance == 50

def test_withdraw_insufficient_balance(setup_accounts):
    result = core.withdraw_from_account("a1", 150)
    assert result is None

def test_transfer_success(setup_accounts):
    origin, dest = core.transfer_between_accounts("a1", "a2", 40)
    assert origin.balance == 60
    assert dest.balance == 90

def test_transfer_insufficient_balance(setup_accounts):
    origin, dest = core.transfer_between_accounts("a1", "a2", 150)
    assert origin is None and dest is None
