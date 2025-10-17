import pytest
from unittest.mock import MagicMock
from src.app.crud import create_user, get_user, create_account, get_account, update_balance
from src.app.schemas import UserCreate, AccountCreate

@pytest.fixture
def mock_db():
    db = MagicMock()
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock()
    return db

def test_create_user(mock_db):
    user_data = UserCreate(name="Test", email="t@example.com", password="123")
    user = create_user(mock_db, user_data)
    assert user.name == "Test"
    mock_db.add.assert_called_once()

def test_get_user(mock_db):
    mock_db.query().filter().first.return_value = "user_obj"
    result = get_user(mock_db, 1)
    assert result == "user_obj"

def test_create_account(mock_db):
    account_data = AccountCreate(id="A", user_id=1)
    acc = create_account(mock_db, account_data)
    assert acc.id == "A"
    mock_db.add.assert_called_once()

def test_get_account(mock_db):
    mock_db.query().filter().first.return_value = "account_obj"
    result = get_account(mock_db, "A")
    assert result == "account_obj"

def test_update_balance(mock_db):
    acc = MagicMock()
    acc.balance = 50
    updated_acc = update_balance(mock_db, acc, 20)
    assert updated_acc.balance == 70
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()
