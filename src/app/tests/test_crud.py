# tests/test_crud.py
import pytest
from sqlalchemy.exc import IntegrityError
from src.app.crud import (
    create_user,
    get_user,
    create_account,
    get_account,
    update_balance,
)
from src.app.schemas import UserCreate, AccountCreate
from src.app.models import User, Account

# ------------------------------------------------------------
# 🔹 FIXTURE : base de données temporaire pour chaque test
# ------------------------------------------------------------
@pytest.fixture
def sample_user(db):
    """Crée un utilisateur en base pour les tests."""
    user_data = UserCreate(name="TestUser", email="testuser@example.com", password="1234")
    return create_user(db, user_data)


# ------------------------------------------------------------
# 🔹 TESTS SUR LA CRÉATION D’UTILISATEUR
# ------------------------------------------------------------
def test_create_user_success(db):
    user_data = UserCreate(name="Alice", email="alice@test.com", password="1234")
    user = create_user(db, user_data)
    assert isinstance(user, User)
    assert user.id is not None
    assert user.name == "Alice"
    assert user.email == "alice@test.com"


def test_create_user_duplicate_email(db):
    user_data = UserCreate(name="Bob", email="bob@test.com", password="1234")
    create_user(db, user_data)
    with pytest.raises(IntegrityError):
        create_user(db, user_data)


def test_get_user_existing(db):
    user_data = UserCreate(name="Carol", email="carol@test.com", password="abcd")
    created = create_user(db, user_data)
    fetched = get_user(db, created.id)
    assert fetched is not None
    assert fetched.email == "carol@test.com"


def test_get_user_not_found(db):
    user = get_user(db, 9999)
    assert user is None


# ------------------------------------------------------------
# 🔹 TESTS SUR LA CRÉATION DE COMPTE
# ------------------------------------------------------------
def test_create_account_success(db, sample_user):
    account_data = AccountCreate(id="acc001", user_id=sample_user.id)
    acc = create_account(db, account_data)
    assert isinstance(acc, Account)
    assert acc.id == "acc001"
    assert acc.owner_id == sample_user.id
    assert acc.balance == 0


def test_create_account_duplicate_id(db, sample_user):
    account_data = AccountCreate(id="acc002", user_id=sample_user.id)
    create_account(db, account_data)
    with pytest.raises(IntegrityError):
        create_account(db, account_data)


def test_create_account_invalid_user(db):
    """Tente de créer un compte avec un user_id inexistant."""
    acc_data = AccountCreate(id="acc007", user_id=9999)
    with pytest.raises(IntegrityError):
        create_account(db, acc_data)


def test_get_account_existing(db, sample_user):
    acc_data = AccountCreate(id="acc003", user_id=sample_user.id)
    created = create_account(db, acc_data)
    fetched = get_account(db, created.id)
    assert fetched is not None
    assert fetched.id == "acc003"
    assert fetched.owner_id == sample_user.id


def test_get_account_not_found(db):
    acc = get_account(db, "unknown")
    assert acc is None


# ------------------------------------------------------------
# 🔹 TESTS SUR LA MISE À JOUR DU SOLDE
# ------------------------------------------------------------
def test_update_balance_positive(db, sample_user):
    acc_data = AccountCreate(id="acc004", user_id=sample_user.id)
    acc = create_account(db, acc_data)
    updated = update_balance(db, acc, 150.0)
    assert updated.balance == 150.0


def test_update_balance_negative(db, sample_user):
    acc_data = AccountCreate(id="acc005", user_id=sample_user.id)
    acc = create_account(db, acc_data)
    update_balance(db, acc, 200.0)
    updated = update_balance(db, acc, -50.0)
    assert updated.balance == 150.0


def test_update_balance_zero(db, sample_user):
    acc_data = AccountCreate(id="acc006", user_id=sample_user.id)
    acc = create_account(db, acc_data)
    old_balance = acc.balance
    updated = update_balance(db, acc, 0.0)
    assert updated.balance == old_balance


def test_update_balance_invalid_account(db):
    """Test de mise à jour sur un compte qui n'est pas lié à la session."""
    fake_acc = Account(id="ghost", owner_id=1, balance=10.0)
    with pytest.raises(Exception):
        update_balance(db, fake_acc, 100.0)
