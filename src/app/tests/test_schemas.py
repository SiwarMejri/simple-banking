# tests/test_schemas.py
import pytest
from src.app.schemas import UserCreate, User, Account, AccountCreate, TransactionCreate, TransactionResponse
from pydantic import ValidationError

def test_user_create_model():
    user = UserCreate(name="Alice", email="alice@example.com", password="123")
    assert user.name == "Alice"
    assert user.email == "alice@example.com"

def test_account_model():
    acc = Account(id="A", balance=100)
    assert acc.id == "A"
    assert acc.balance == 100

def test_account_create_model():
    account = AccountCreate(id="A2", user_id=1)
    assert account.id == "A2"
    assert account.user_id == 1

def test_transaction_create_valid():
    tx = TransactionCreate(type="deposit", destination="A", amount=50)
    assert tx.amount == 50

def test_transaction_create_invalid():
    with pytest.raises(ValidationError):
        TransactionCreate(type="deposit", destination="A", amount="invalid")

def test_transaction_response():
    resp = TransactionResponse(type="withdraw")
    assert resp.type == "withdraw"
