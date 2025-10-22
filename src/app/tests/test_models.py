import pytest
from pydantic import ValidationError
from models import User, Account, Transaction  # Test des imports
from schemas import (
    UserCreate, User, AccountCreate, AccountSchema, TransactionCreate, TransactionResponse
)

# Tests pour modèles (imports)
def test_models_imports():
    # Vérifie que les imports fonctionnent
    assert User
    assert Account
    assert Transaction

# Tests pour schémas Pydantic
def test_user_create_valid():
    user = UserCreate(name="test", email="test@example.com", password="pass")
    assert user.name == "test"
    assert user.email == "test@example.com"

def test_user_create_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(name="test", email="invalid", password="pass")

def test_user_create_missing_field():
    with pytest.raises(ValidationError):
        UserCreate(name="test", email="test@example.com")  # password manquant

def test_account_create_valid():
    acc = AccountCreate(id="acc1", balance=100.0)
    assert acc.id == "acc1"
    assert acc.balance == 100.0

def test_account_create_negative_balance():
    with pytest.raises(ValidationError):
        AccountCreate(id="acc1", balance=-10.0)

def test_transaction_create_valid():
    trans = TransactionCreate(type="deposit", destination="acc1", amount=50.0)
    assert trans.type == "deposit"
    assert trans.amount == 50.0

def test_transaction_create_invalid_type():
    with pytest.raises(ValidationError):
        TransactionCreate(type="invalid", destination="acc1", amount=50.0)

def test_transaction_create_zero_amount():
    with pytest.raises(ValidationError):
        TransactionCreate(type="deposit", destination="acc1", amount=0)

def test_transaction_response():
    resp = TransactionResponse(type="deposit", origin=None, destination=AccountSchema(id="acc1", balance=100.0, owner_id=1))
    assert resp.type == "deposit"
    assert resp.destination.id == "acc1"

def test_account_schema():
    acc = AccountSchema(id="acc1", balance=100.0, owner_id=1)
    assert acc.id == "acc1"
    assert acc.balance == 100.0
