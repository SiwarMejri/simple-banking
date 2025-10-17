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
import pytest
from src.app.models.schemas import UserCreate, User, Account, AccountCreate, TransactionCreate, TransactionResponse

def test_user_create_model():
    user = UserCreate(name="Alice", email="alice@example.com", password="123")
    assert user.name == "Alice"
    assert user.email == "alice@example.com"
    assert user.password == "123"

def test_user_model_with_accounts():
    account = Account(id="A1", balance=100)
    user = User(id=1, name="Bob", email="bob@example.com", accounts=[account])
    assert user.id == 1
    assert user.accounts[0].id == "A1"
    assert user.accounts[0].balance == 100

def test_account_create_model():
    account = AccountCreate(id="A2", user_id=1)
    assert account.id == "A2"
    assert account.user_id == 1

def test_transaction_models():
    t_create = TransactionCreate(type="deposit", origin="A", destination="B", amount=50)
    assert t_create.type == "deposit"
    assert t_create.amount == 50
    assert t_create.origin == "A"
    assert t_create.destination == "B"

    t_response = TransactionResponse(type="withdraw")
    assert t_response.type == "withdraw"
 
