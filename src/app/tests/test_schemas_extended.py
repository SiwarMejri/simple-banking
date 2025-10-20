import pytest
from pydantic import ValidationError
from src.app.schemas import UserCreate, User, Account, AccountCreate, TransactionCreate, TransactionResponse

def test_user_create_model_invalid_missing_field():
    # Test sans champ requis password
    with pytest.raises(ValidationError):
        UserCreate(name="Bob", email="bob@example.com")

def test_account_model_invalid_balance_type():
    # Test balance non entier
    with pytest.raises(ValidationError):
        Account(id="A1", balance="not_an_int")

def test_transaction_create_missing_required_type():
    with pytest.raises(ValidationError):
        TransactionCreate(amount=100)

def test_user_accounts_default_empty_list():
    user = User(id=1, name="Alice", email="alice@example.com")
    assert user.accounts == []

def test_transaction_response_with_accounts():
    origin_acc = Account(id="O1", balance=100)
    dest_acc = Account(id="D1", balance=50)
    resp = TransactionResponse(type="transfer", origin=origin_acc, destination=dest_acc)
    assert resp.origin.id == "O1"
    assert resp.destination.id == "D1"
