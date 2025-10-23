# tests/test_crud.py
import pytest
from sqlalchemy.orm import Session
from src.app.models.user import UserModel
from src.app.models.account import AccountModel  
from src.app.models.transaction import TransactionModel
from crud import (
    get_user, get_users, create_user, get_account, get_accounts, create_account,
    get_transaction, get_transactions, create_transaction
)
from schemas import UserCreate, AccountCreate


def test_get_user(db: Session):
    # Test récupération d'un utilisateur existant
    user = UserModel(name="test", email="test@example.com", password="plain_password")
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
    user1 = UserModel(name="test1", email="test1@example.com", password="password1")
    user2 = UserModel(name="test2", email="test2@example.com", password="password2")
    db.add(user1)
    db.add(user2)
    db.commit()
    
    result = get_users(db)
    user_emails = [user.email for user in result]
    assert "test1@example.com" in user_emails
    assert "test2@example.com" in user_emails


def test_create_user(db: Session):
    # Test création utilisateur
    user_data = UserCreate(name="newuser", email="new@example.com", password="pass")
    result = create_user(db, user_data)
    assert result.name == "newuser"
    assert result.email == "new@example.com"
    assert hasattr(result, 'password')


def test_get_account(db: Session):
    # Test récupération compte - créer d'abord un utilisateur
    test_user = UserModel(name="owner", email="owner@example.com", password="pass")
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    
    account = AccountModel(id="acc1", balance=100.0, owner_id=test_user.id)
    db.add(account)
    db.commit()
    
    result = get_account(db, "acc1")
    assert result.id == "acc1"
    assert result.balance == 100.0


def test_get_account_not_found(db: Session):
    # Test compte inexistant
    result = get_account(db, "nonexistent")
    assert result is None


def test_get_accounts(db: Session):
    # Test liste comptes - créer d'abord un utilisateur
    test_user = UserModel(name="owner", email="owner@example.com", password="pass")
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    
    acc1 = AccountModel(id="acc1", balance=100.0, owner_id=test_user.id)
    acc2 = AccountModel(id="acc2", balance=200.0, owner_id=test_user.id)
    db.add(acc1)
    db.add(acc2)
    db.commit()
    
    result = get_accounts(db)
    account_ids = [acc.id for acc in result]
    assert "acc1" in account_ids
    assert "acc2" in account_ids


def test_create_account(db: Session):
    # Test création compte - créer d'abord un utilisateur
    test_user = UserModel(name="testuser", email="testuser@example.com", password="testpass")
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    
    account_data = AccountCreate(id="newacc", balance=50.0, user_id=test_user.id)
    result = create_account(db, account_data, user_id=test_user.id)
    assert result.id == "newacc"
    assert result.balance == 50.0
    assert result.owner_id == test_user.id


def test_get_transaction(db: Session):
    # Test récupération transaction - CORRECTION : utiliser account_id
    trans = TransactionModel(type="deposit", amount=100.0, account_id="acc1")
    db.add(trans)
    db.commit()
    db.refresh(trans)
    
    result = get_transaction(db, trans.id)
    assert result.id == trans.id
    assert result.type == "deposit"


def test_get_transaction_not_found(db: Session):
    # Test transaction inexistante
    result = get_transaction(db, 999)
    assert result is None


def test_get_transactions(db: Session):
    # Test liste transactions - CORRECTION : utiliser account_id
    trans1 = TransactionModel(type="deposit", amount=100.0, account_id="acc1")
    trans2 = TransactionModel(type="withdraw", amount=50.0, account_id="acc1")
    db.add(trans1)
    db.add(trans2)
    db.commit()
    
    result = get_transactions(db)
    assert len(result) >= 2
    transaction_types = [trans.type for trans in result]
    assert "deposit" in transaction_types
    assert "withdraw" in transaction_types


def test_create_transaction(db: Session):
    # Test création transaction - CORRECTION : utiliser account_id
    trans_data = {"type": "deposit", "amount": 200.0, "account_id": "acc1"}
    result = create_transaction(db, trans_data)
    assert result.type == "deposit"
    assert result.amount == 200.0
    assert result.account_id == "acc1"
