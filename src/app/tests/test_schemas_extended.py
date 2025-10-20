import pytest
from pydantic import ValidationError
from src.app.schemas import User, UserCreate, Account, AccountCreate, TransactionCreate, TransactionResponse


def test_user_full_model_from_attributes():
    """Test complet du modèle User avec des comptes liés."""
    account = Account(id="acc1", balance=200)
    user = User(id=1, name="Siwar", email="siwar@example.com", accounts=[account])
    assert user.id == 1
    assert user.accounts[0].balance == 200
    assert user.model_dump()["name"] == "Siwar"


def test_account_create_and_repr():
    """Test simple de AccountCreate."""
    acc = AccountCreate(id="A10", user_id=10)
    assert acc.id == "A10"
    assert acc.user_id == 10


def test_transaction_create_all_fields():
    tx = TransactionCreate(type="transfer", origin="a1", destination="a2", amount=50)
    assert tx.origin == "a1"
    assert tx.destination == "a2"
    assert tx.amount == 50


def test_transaction_create_invalid_amount_type():
    """Déclenche une erreur Pydantic sur type de montant invalide."""
    with pytest.raises(ValidationError):
        TransactionCreate(type="deposit", amount="abc")


def test_transaction_response_with_accounts():
    origin = Account(id="a1", balance=10)
    dest = Account(id="a2", balance=20)
    txr = TransactionResponse(type="transfer", origin=origin, destination=dest)
    assert txr.origin.balance == 10
    assert txr.destination.id == "a2"
