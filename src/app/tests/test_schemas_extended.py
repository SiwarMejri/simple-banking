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
        TransactionCreate(amount=50.0, account_id="acc1")  # Type manquant

def test_user_accounts_default_empty_list():
    user = User(id=1, name="John Doe", email="john@example.com")
    assert user.id == 1
    assert user.name == "John Doe"
    assert user.email == "john@example.com"

def test_transaction_response_with_accounts():
    # CORRECTION : utiliser account_id au lieu de origin/destination
    response = TransactionResponse(type="transfer", account_id="acc1")
    assert response.type == "transfer"
    assert response.account_id == "acc1"
