import pytest
from pydantic import ValidationError

def test_models_imports():
    # Test que les modèles s'importent correctement
    from src.app.models import UserModel, AccountModel, TransactionModel
    assert True  # Si on arrive ici, l'import a réussi

def test_user_create_valid():
    from schemas import UserCreate
    # Test création utilisateur valide
    user = UserCreate(name="test", email="valid@example.com", password="password123")
    assert user.name == "test"
    assert user.email == "valid@example.com"

def test_user_create_invalid_email():
    from schemas import UserCreate
    # Test avec un email vraiment invalide
    with pytest.raises(ValueError):
        UserCreate(name="test", email="not-an-email", password="pass")

def test_user_create_missing_field():
    from schemas import UserCreate
    # Test champ manquant
    with pytest.raises(ValidationError):
        UserCreate(name="test")  # email et password manquants

def test_account_create_valid():
    from schemas import AccountCreate
    # Test création compte valide
    acc = AccountCreate(id="acc1", balance=100.0, user_id=1)
    assert acc.id == "acc1"
    assert acc.balance == 100.0
    assert acc.user_id == 1

def test_account_create_negative_balance():
    from schemas import AccountCreate
    # Test solde négatif (devrait être autorisé selon votre schéma)
    acc = AccountCreate(id="acc1", balance=-50.0, user_id=1)
    assert acc.balance == -50.0

def test_transaction_create_valid():
    from schemas import TransactionCreate
    # Test création transaction valide
    trans = TransactionCreate(type="deposit", amount=100.0, destination="acc1")
    assert trans.type == "deposit"
    assert trans.amount == 100.0

def test_transaction_create_invalid_type():
    from schemas import TransactionCreate
    # Test type vide (doit déclencher ValidationError via le validateur)
    with pytest.raises(ValueError):
        TransactionCreate(type="", amount=100.0)

def test_transaction_create_zero_amount():
    from schemas import TransactionCreate
    # Test montant zéro (doit déclencher ValidationError)
    with pytest.raises(ValueError):
        TransactionCreate(type="deposit", amount=0)

def test_transaction_response():
    from schemas import TransactionResponse, AccountSchema
    from datetime import datetime
    # Test réponse de transaction
    account = AccountSchema(id="acc1", balance=100.0, owner_id=1)
    response = TransactionResponse(
        type="deposit",
        destination=account
    )
    assert response.type == "deposit"
    assert response.destination.id == "acc1"

def test_account_schema():
    from schemas import AccountSchema
    # Test schéma compte
    account = AccountSchema(id="acc1", balance=150.0, owner_id=1)
    assert account.id == "acc1"
    assert account.balance == 150.0
    assert account.owner_id == 1
