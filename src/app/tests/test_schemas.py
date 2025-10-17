import pytest
from src.app.schemas import Account, UserCreate, TransactionCreate
from pydantic import ValidationError

def test_account_model():
    acc = Account(id="A", balance=100)
    assert acc.id == "A"
    assert acc.balance == 100

def test_user_create_model():
    user = UserCreate(name="Test", email="test@example.com", password="1234")
    assert user.name == "Test"
    assert user.email == "test@example.com"

def test_transaction_create_valid():
    tx = TransactionCreate(type="deposit", destination="A", amount=50)
    assert tx.amount == 50

def test_transaction_create_invalid_amount():
    with pytest.raises(ValidationError):
        TransactionCreate(type="deposit", amount="invalid")
