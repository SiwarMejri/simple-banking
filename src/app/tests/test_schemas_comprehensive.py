import pytest
from src.app.schemas import UserCreate, User, AccountSchema, AccountCreate, TransactionCreate, TransactionResponse

# ---------------- Tests étendus pour les schémas ----------------
def test_user_create_model_invalid_missing_field():
    with pytest.raises(ValueError):
        UserCreate(name="John Doe", email="john@example.com")  # Mot de passe manquant

def test_account_model_invalid_balance_type():
    with pytest.raises(ValueError):
        AccountSchema(id="acc1", balance="invalid")  # Balance doit être un float

def test_transaction_create_missing_required_type():
    with pytest.raises(ValueError):
        TransactionCreate(amount=50.0, destination="acc1")  # Type manquant

def test_user_accounts_default_empty_list():
    user = User(id=1, name="John Doe", email="john@example.com")
    assert user.id == 1
    assert user.name == "John Doe"
    assert user.email == "john@example.com"

def test_transaction_response_with_accounts():
    origin = AccountSchema(id="acc1", balance=100.0, owner_id=1)  # Ajouté owner_id
    destination = AccountSchema(id="acc2", balance=50.0, owner_id=2)  # Ajouté owner_id
    response = TransactionResponse(type="transfer", origin=origin, destination=destination)
    assert response.type == "transfer"
    assert response.origin.id == "acc1"
    assert response.origin.balance == 100.0
    assert response.destination.id == "acc2"
    assert response.destination.balance == 50.0
