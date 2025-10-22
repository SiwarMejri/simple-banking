# src/app/tests/test_schemas_corrected.py
import pytest
from pydantic import ValidationError
from datetime import datetime

from src.app.models.schemas import (
    UserBase, UserCreate, User,
    AccountBase, AccountCreate, Account,
    TransactionCreate, TransactionResponse
)


class TestAccountSchemasCorrected:
    """Tests corrigés pour les schémas Account"""
    
    def test_account_base_valid(self):
        """Test AccountBase avec données valides"""
        data = {"id": "ACC123", "balance": 1000.0}
        account = AccountBase(**data)
        
        assert account.id == "ACC123"
        assert account.balance == 1000.0
    
    def test_account_create_valid(self):
        """Test AccountCreate avec données valides"""
        data = {
            "id": "ACC123",
            "balance": 1000.0,
            "user_id": 1
        }
        account = AccountCreate(**data)
        
        assert account.id == "ACC123"
        assert account.balance == 1000.0
        assert account.user_id == 1
    
    def test_account_schema_owner_id_required(self):
        """Test que Account requiert owner_id"""
        data = {"id": "ACC123", "balance": 1000.0}
        
        # Doit échouer car owner_id est requis
        with pytest.raises(ValidationError) as exc_info:
            Account(**data)
        
        assert "owner_id" in str(exc_info.value)
    
    def test_account_schema_with_owner_id(self):
        """Test Account avec owner_id"""
        data = {
            "id": "ACC123", 
            "balance": 1000.0,
            "owner_id": 1
        }
        account = Account(**data)
        
        assert account.id == "ACC123"
        assert account.balance == 1000.0
        assert account.owner_id == 1
