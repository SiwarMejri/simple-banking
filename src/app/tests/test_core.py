# tests/test_core.py
import pytest
from src.app.core import core
from src.app.models.account import Account

# ---------------- Fixtures ----------------
@pytest.fixture
def setup_accounts():
    """Initialise deux comptes en mémoire avant chaque test."""
    core.reset_state()
    core.create_or_update_account("a1", 100)
    core.create_or_update_account("a2", 50)
    yield
    core.reset_state()


# ---------------- Tests pour les fonctions en mémoire ----------------
def test_create_or_update_account_new():
    core.reset_state()
    acc = core.create_or_update_account("u1", 200)
    assert acc.balance == 200

def test_create_or_update_account_existing():
    core.reset_state()
    core.create_or_update_account("u1", 100)
    acc = core.create_or_update_account("u1", 50)
    assert acc.balance == 150

def test_withdraw_from_account_success(setup_accounts):
    result = core.withdraw_from_account("a1", 30)
    assert result.balance == 70

def test_withdraw_from_account_insufficient(setup_accounts):
    assert core.withdraw_from_account("a2", 100) is None

def test_withdraw_from_account_not_found():
    assert core.withdraw_from_account("xyz", 10) is None

def test_withdraw_from_account_zero_amount(setup_accounts):
    result = core.withdraw_from_account("a1", 0)
    assert result.balance == 100

def test_transfer_between_accounts_success(setup_accounts):
    origin, dest = core.transfer_between_accounts("a1", "a2", 20)
    assert origin.balance == 80
    assert dest.balance == 70

def test_transfer_between_accounts_insufficient(setup_accounts):
    origin, dest = core.transfer_between_accounts("a2", "a1", 200)
    assert origin is None and dest is None

def test_transfer_between_accounts_new_destination(setup_accounts):
    origin, dest = core.transfer_between_accounts("a1", "a3", 50)
    assert origin.balance == 50
    assert dest.balance == 50


# ---------------- Tests pour la fonction transfer_money (base de données) ----------------
def test_transfer_money_valid(mocker):
    db = mocker.Mock()
    sender = Account(id="a1", balance=100)
    receiver = Account(id="a2", balance=50)
    assert core.transfer_money(db, sender, receiver, 30)
    assert sender.balance == 70
    assert receiver.balance == 80

def test_transfer_money_insufficient_balance(mocker):
    db = mocker.Mock()
    sender = Account(id="a1", balance=10)
    receiver = Account(id="a2", balance=50)
    with pytest.raises(ValueError, match="Solde insuffisant"):
        core.transfer_money(db, sender, receiver, 100)

def test_transfer_money_zero_amount(mocker):
    db = mocker.Mock()
    sender = Account(id="a1", balance=100)
    receiver = Account(id="a2", balance=50)
    assert core.transfer_money(db, sender, receiver, 0)
    assert sender.balance == 100
    assert receiver.balance == 50


# ---------------- Tests pour la fonction process_transaction ----------------
def test_process_transaction_success(mocker):
    db = mocker.Mock()
    sender = Account(id="1", balance=200)
    receiver = Account(id="2", balance=100)
    db.query().filter().first.side_effect = [sender, receiver]

    data = {"from_account": "1", "to_account": "2", "amount": 50}
    result = core.process_transaction(db, data)
    assert result["status"] == "success"
    assert sender.balance == 150
    assert receiver.balance == 150

def test_process_transaction_insufficient_balance(mocker):
    db = mocker.Mock()
    sender = Account(id="1", balance=10)
    receiver = Account(id="2", balance=100)
    db.query().filter().first.side_effect = [sender, receiver]

    data = {"from_account": "1", "to_account": "2", "amount": 100}
    result = core.process_transaction(db, data)
    assert result["status"] == "failed"
    assert "Solde insuffisant" in result["reason"]

def test_process_transaction_invalid_accounts(mocker):
    db = mocker.Mock()
    db.query().filter().first.side_effect = [None, None]
    data = {"from_account": "x", "to_account": "y", "amount": 10}
    result = core.process_transaction(db, data)
    assert result["status"] == "failed"
    assert "n'existe pas" in result["reason"]

def test_process_transaction_missing_fields(mocker):
    db = mocker.Mock()
    data = {"from_account": "1", "amount": 10}  # to_account manquant
    result = core.process_transaction(db, data)
    assert result["status"] == "failed"
    assert "paramètres manquants" in result["reason"]

def test_process_transaction_zero_amount(mocker):
    db = mocker.Mock()
    sender = Account(id="1", balance=100)
    receiver = Account(id="2", balance=50)
    db.query().filter().first.side_effect = [sender, receiver]
    data = {"from_account": "1", "to_account": "2", "amount": 0}
    result = core.process_transaction(db, data)
    assert result["status"] == "success"
    assert sender.balance == 100
    assert receiver.balance == 50
