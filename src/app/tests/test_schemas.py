import pytest
from src.app.schemas import UserCreate, User, AccountSchema, AccountCreate, TransactionCreate, TransactionResponse

# ---------------- Tests pour les schémas ----------------
def test_user_create_model():
    user = UserCreate(name="John Doe", email="john@example.com", password="secret")
    assert user.name == "John Doe"
    assert user.email == "john@example.com"
    assert user.password == "secret"

def test_user_model():
    user = User(id=1, name="John Doe", email="john@example.com")
    assert user.id == 1
    assert user.name == "John Doe"
    assert user.email == "john@example.com"

def test_account_model():
    account = AccountSchema(id="acc1", balance=100.0, owner_id=1)  # Ajouté owner_id
    assert account.id == "acc1"
    assert account.balance == 100.0
    assert account.owner_id == 1

def test_account_create_model():
    account = AccountCreate(id="acc1", user_id=1)
    assert account.id == "acc1"
    assert account.user_id == 1

def test_transaction_create_valid():
    transaction = TransactionCreate(type="deposit", amount=50.0, destination="acc1")
    assert transaction.type == "deposit"
    assert transaction.amount == 50.0
    assert transaction.destination == "acc1"

def test_transaction_create_invalid():
    with pytest.raises(ValueError):
        TransactionCreate(type="", amount=-10.0)  # Type vide et montant négatif

def test_transaction_response():
    response = TransactionResponse(type="deposit", origin=None, destination=AccountSchema(id="acc1", balance=50.0, owner_id=1))  # Ajouté owner_id
    assert response.type == "deposit"
    assert response.origin is None
    assert response.destination.id == "acc1"
    assert response.destination.balance == 50.0
