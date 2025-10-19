# tests/test_core.py
import pytest
from src.app.core.core import transfer_money, process_transaction
from src.app.crud import create_user, create_account
from src.app.schemas import UserCreate, AccountCreate
from src.app.core import core
from src.app.models.account import Account

@pytest.fixture
def setup_accounts():
    core.reset_state()
    core.create_or_update_account("a1", 100)
    core.create_or_update_account("a2", 50)
    yield
    core.reset_state()

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

def test_transfer_between_accounts_success(setup_accounts):
    origin, dest = core.transfer_between_accounts("a1", "a2", 20)
    assert origin.balance == 80
    assert dest.balance == 70

def test_transfer_between_accounts_insufficient(setup_accounts):
    origin, dest = core.transfer_between_accounts("a2", "a1", 200)
    assert origin is None and dest is None

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

def test_transfer_money(db):
    user1 = create_user(db, UserCreate(name="A", email="a@test.com", password="123"))
    user2 = create_user(db, UserCreate(name="B", email="b@test.com", password="123"))
    acc1 = create_account(db, AccountCreate(id="acc1", user_id=user1.id))
    acc2 = create_account(db, AccountCreate(id="acc2", user_id=user2.id))

    # Ajouter de l'argent sur le compte 1
    acc1.balance = 500
    db.commit()

    # Transfert de 200
    transfer_money(db, acc1, acc2, 200)
    db.refresh(acc1)
    db.refresh(acc2)
    assert acc1.balance == 300
    assert acc2.balance == 200

    # Test transfert > solde
    with pytest.raises(ValueError):
        transfer_money(db, acc1, acc2, 400)
