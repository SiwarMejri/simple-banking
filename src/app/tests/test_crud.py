# tests/test_crud.py
import pytest
from src.app.crud import create_user, get_user, create_account, get_account, update_balance
from src.app.schemas import UserCreate, AccountCreate
from src.app import crud
from src.app.models import schemas

@pytest.mark.parametrize("user_id,name,email", [(1, "Siwar", "siwar@example.com")])
def test_create_user(mocker, user_id, name, email):
    db = mocker.Mock()
    user_data = schemas.UserCreate(name=name, email=email, password="1234")
    mock_user = mocker.Mock(id=user_id, name=name, email=email)
    db.add.return_value = None
    db.commit.return_value = None
    db.refresh.return_value = None
    crud.create_user(db, user_data)
    db.add.assert_called_once()

def test_get_user_by_email(mocker):
    db = mocker.Mock()
    crud.get_user_by_email(db, "test@example.com")
    db.query.assert_called_once()
def test_create_user(db):
    user_data = UserCreate(name="Alice", email="alice@test.com", password="1234")
    user = create_user(db, user_data)
    assert user.id is not None
    assert user.name == "Alice"
    assert user.email == "alice@test.com"

def test_get_user(db):
    user_data = UserCreate(name="Bob", email="bob@test.com", password="1234")
    created = create_user(db, user_data)
    fetched = get_user(db, created.id)
    assert fetched.email == "bob@test.com"

def test_create_account(db):
    user_data = UserCreate(name="Charlie", email="charlie@test.com", password="1234")
    user = create_user(db, user_data)
    account_data = AccountCreate(id="acc123", user_id=user.id)
    account = create_account(db, account_data)
    assert account.id == "acc123"
    assert account.owner_id == user.id
    assert account.balance == 0

def test_get_account(db):
    user_data = UserCreate(name="David", email="david@test.com", password="1234")
    user = create_user(db, user_data)
    account_data = AccountCreate(id="acc456", user_id=user.id)
    create_account(db, account_data)
    fetched = get_account(db, "acc456")
    assert fetched.owner_id == user.id

def test_update_balance(db):
    user_data = UserCreate(name="Eve", email="eve@test.com", password="1234")
    user = create_user(db, user_data)
    account_data = AccountCreate(id="acc789", user_id=user.id)
    account = create_account(db, account_data)
    updated = update_balance(db, account, 100.0)
    assert updated.balance == 100.0
    updated = update_balance(db, account, -50.0)
    assert updated.balance == 50.0
