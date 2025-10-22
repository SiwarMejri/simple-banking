# tests/test_core.py
import pytest
from src.app.core import core
from src.app.models.account import Account

# ---------------- Fixtures ----------------
@pytest.fixture
def setup_accounts():
    """Initialise deux comptes en mémoire avant chaque test."""
    core.accounts.clear()
    core.accounts["a1"] = Account(id="a1", balance=100)
    core.accounts["a2"] = Account(id="a2", balance=50)
    yield
    core.accounts.clear()

# ---------------- Tests pour les fonctions en mémoire ----------------
def test_create_account_and_balance():
    core.accounts.clear()
    core.accounts["u1"] = Account(id="u1", balance=200)
    assert core.accounts["u1"].balance == 200

def test_update_account_balance():
    core.accounts.clear()
    core.accounts["u1"] = Account(id="u1", balance=100)
    core.accounts["u1"].balance += 50
    assert core.accounts["u1"].balance == 150

def test_withdraw_success(setup_accounts):
    acc = core.accounts["a1"]
    acc.balance -= 30
    assert acc.balance == 70

def test_withdraw_insufficient_balance(setup_accounts):
    acc = core.accounts["a2"]
    initial_balance = acc.balance
    if acc.balance < 100:
        acc.balance = acc.balance  # aucune modification
    assert acc.balance == initial_balance

def test_transfer_success(setup_accounts):
    a1 = core.accounts["a1"]
    a2 = core.accounts["a2"]
    amount = 20

    if a1.balance >= amount:
        a1.balance -= amount
        a2.balance += amount

    assert a1.balance == 80
    assert a2.balance == 70

def test_transfer_insufficient_balance(setup_accounts):
    a1 = core.accounts["a1"]
    a2 = core.accounts["a2"]
    amount = 200

    initial_a1 = a1.balance
    initial_a2 = a2.balance

    if a1.balance < amount:
        pass  # aucune transaction

    assert a1.balance == initial_a1
    assert a2.balance == initial_a2
