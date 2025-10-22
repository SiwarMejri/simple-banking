# tests/conftest.py
import pytest
from sqlalchemy.orm import Session
from models import User, Account, Transaction
from crud import (
    get_user, get_users, create_user, get_account, get_accounts, create_account,
    get_transaction, get_transactions, create_transaction
)
from schemas import UserCreate, AccountCreate

def test_get_user(db: Session):
    # Test récupération d'un utilisateur existant
    user = User(name="test", email="test@example.com", hashed_password="hashed")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    result = get_user(db, user.id)
    assert result == user

def test_get_user_not_found(db: Session):
    # Test utilisateur inexistant
    result = get_user(db, 999)
    assert result is None

def test_get_users(db: Session):
    # Test liste d'utilisateurs
    user1 = User(name="test1", email="test1@example.com", hashed_password="hashed")
    user2 = User(name="test2", email="test2@example.com", hashed_password="hashed")
    db.add(user1)
    db.add(user2)
    db.commit()
    
    result = get_users(db)
    assert len(result) == 2
    assert result[0].name == "test1"

def test_create_user(db: Session):
    # Test création utilisateur
    user_data = UserCreate(name="newuser", email="new@example.com", password="pass")
    result = create_user(db, user_data)
    assert result.name == "newuser"
    assert result.email == "new@example.com"

def test_get_account(db: Session):
    # Test récupération compte
    account = Account(id="acc1", balance=100.0, owner_id=1)
    db.add(account)
    db.commit()
    
    result = get_account(db, "acc1")
    assert result == account

def test_get_account_not_found(db: Session):
    # Test compte inexistant
    result = get_account(db, "nonexistent")
    assert result is None

def test_get_accounts(db: Session):
    # Test liste comptes
    acc1 = Account(id="acc1", balance=100.0, owner_id=1)
    acc2 = Account(id="acc2", balance=200.0, owner_id=1)
    db.add(acc1)
    db.add(acc2)
    db.commit()
    
    result = get_accounts(db)
    assert len(result) == 2

def test_create_account(db: Session):
    # Test création compte
    account_data = AccountCreate(id="newacc", balance=50.0)
    result = create_account(db, account_data, user_id=1)
    assert result.id == "newacc"
    assert result.balance == 50.0
    assert result.owner_id == 1

def test_get_transaction(db: Session):
    # Test récupération transaction
    trans = Transaction(type="deposit", amount=100.0, origin=None, destination="acc1")
    db.add(trans)
    db.commit()
    db.refresh(trans)
    
    result = get_transaction(db, trans.id)
    assert result == trans

def test_get_transaction_not_found(db: Session):
    # Test transaction inexistante
    result = get_transaction(db, 999)
    assert result is None

def test_get_transactions(db: Session):
    # Test liste transactions
    trans1 = Transaction(type="deposit", amount=100.0, origin=None, destination="acc1")
    trans2 = Transaction(type="withdraw", amount=50.0, origin="acc1", destination=None)
    db.add(trans1)
    db.add(trans2)
    db.commit()
    
    result = get_transactions(db)
    assert len(result) == 2

def test_create_transaction(db: Session):
    # Test création transaction
    trans_data = {"type": "deposit", "amount": 200.0, "origin": None, "destination": "acc1"}
    result = create_transaction(db, trans_data)
    assert result.type == "deposit"
    assert result.amount == 200.0
    assert result.destination == "acc1"
