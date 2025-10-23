import pytest
from pydantic import ValidationError
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.app.models.schemas import (
    UserBase, UserCreate, User,
    AccountBase, AccountCreate, AccountSchema,
    TransactionCreate, TransactionResponse,
    TransactionType
)

class TestSchemasComprehensive:
    """Tests complets pour tous les schémas"""
    
    # Tests UserBase
    def test_user_base_valid(self):
        data = {"name": "John", "email": "john@test.com"}
        user = UserBase(**data)
        assert user.name == "John"
        assert user.email == "john@test.com"
    
    def test_user_base_invalid_name(self):
        with pytest.raises(ValidationError):
            UserBase(name="", email="test@test.com")
    
    # Tests UserCreate
    def test_user_create_valid(self):
        data = {"name": "John", "email": "john@test.com", "password": "secret"}
        user = UserCreate(**data)
        assert user.password == "secret"
    
    def test_user_create_invalid_password(self):
        with pytest.raises(ValidationError):
            UserCreate(name="John", email="test@test.com", password="")
    
    # Tests User
    def test_user_with_accounts(self):
        data = {"id": 1, "name": "John", "email": "test@test.com"}
        user = User(**data)
        assert user.accounts == []
    
    # Tests AccountBase
    def test_account_base_default_balance(self):
        data = {"id": "acc1"}
        account = AccountBase(**data)
        assert account.balance == 0.0
    
    def test_account_base_custom_balance(self):
        data = {"id": "acc1", "balance": 100.0}
        account = AccountBase(**data)
        assert account.balance == 100.0
    
    # Tests AccountCreate
    def test_account_create_valid(self):
        data = {"id": "acc1", "balance": 100.0, "user_id": 1}
        account = AccountCreate(**data)
        assert account.user_id == 1
    
    def test_account_create_invalid_user_id(self):
        with pytest.raises(ValidationError):
            AccountCreate(id="acc1", balance=100.0, user_id=0)
    
    # Tests AccountSchema
    def test_account_schema_valid(self):
        data = {"id": "acc1", "balance": 100.0, "owner_id": 1}
        account = AccountSchema(**data)
        assert account.owner_id == 1
    
    def test_account_schema_missing_owner_id(self):
        with pytest.raises(ValidationError):
            AccountSchema(id="acc1", balance=100.0)
    
    # Tests TransactionCreate
    def test_transaction_create_enum_types(self):
        for tx_type in TransactionType:
            data = {"type": tx_type, "amount": 100.0, "account_id": "acc1"}
            transaction = TransactionCreate(**data)
            assert transaction.type == tx_type
    
    def test_transaction_create_string_types(self):
        data = {"type": "deposit", "amount": 100.0, "account_id": "acc1"}
        transaction = TransactionCreate(**data)
        assert transaction.type == "deposit"
    
    def test_transaction_create_invalid_amount(self):
        with pytest.raises(ValidationError):
            TransactionCreate(type="deposit", amount=0, account_id="acc1")
    
    # Tests TransactionResponse
    def test_transaction_response_defaults(self):
        data = {"type": "deposit", "account_id": "acc1"}
        response = TransactionResponse(**data)
        assert response.status == "success"
        assert isinstance(response.timestamp, datetime)
    
    def test_transaction_response_custom_status(self):
        data = {"type": "deposit", "account_id": "acc1", "status": "failed"}
        response = TransactionResponse(**data)
        assert response.status == "failed"
