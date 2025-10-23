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
    # CORRECTION : utiliser account_id au lieu de destination
    transaction = TransactionCreate(type="deposit", amount=50.0, account_id="acc1")
    assert transaction.type == "deposit"
    assert transaction.amount == 50.0
    assert transaction.account_id == "acc1"

def test_transaction_create_invalid():
    with pytest.raises(ValueError):
        TransactionCreate(type="", amount=-10.0)  # Type vide et montant négatif

def test_transaction_response():
    # CORRECTION : utiliser account_id au lieu de origin/destination
    response = TransactionResponse(type="deposit", account_id="acc1")
    assert response.type == "deposit"
    assert response.account_id == "acc1"
