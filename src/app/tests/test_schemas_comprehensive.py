# src/app/tests/test_schemas_comprehensive.py
import pytest
from pydantic import ValidationError
from datetime import datetime

from src.app.schemas import (
    UserBase, UserCreate, User,
    AccountBase, AccountCreate, AccountSchema,
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
        """Test que AccountSchema requiert owner_id"""
        data = {"id": "ACC123", "balance": 1000.0}
        
        # Doit échouer car owner_id est requis
        with pytest.raises(ValidationError) as exc_info:
            AccountSchema(**data)
        
        assert "owner_id" in str(exc_info.value)
    
    def test_account_schema_with_owner_id(self):
        """Test AccountSchema avec owner_id"""
        data = {
            "id": "ACC123", 
            "balance": 1000.0,
            "owner_id": 1
        }
        account = AccountSchema(**data)
        
        assert account.id == "ACC123"
        assert account.balance == 1000.0
        assert account.owner_id == 1


class TestUserSchemasComprehensive:
    """Tests complets pour les schémas User"""
    
    def test_user_base_valid(self):
        """Test UserBase avec données valides"""
        data = {"name": "John Doe", "email": "john@example.com"}
        user = UserBase(**data)
        
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
    
    def test_user_create_valid(self):
        """Test UserCreate avec données valides"""
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "secret123"
        }
        user = UserCreate(**data)
        
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.password == "secret123"
    
    def test_user_create_invalid_email(self):
        """Test UserCreate avec email invalide"""
        data = {
            "name": "John Doe",
            "email": "invalid-email",
            "password": "secret123"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)
        
        assert "email" in str(exc_info.value)
    
    def test_user_model_valid(self):
        """Test User avec données valides"""
        data = {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com"
        }
        user = User(**data)
        
        assert user.id == 1
        assert user.name == "John Doe"
        assert user.email == "john@example.com"


class TestTransactionSchemasComprehensive:
    """Tests complets pour les schémas Transaction"""
    
    def test_transaction_create_deposit_valid(self):
        """Test TransactionCreate pour un dépôt valide"""
        data = {
            "type": "deposit",
            "amount": 100.0,
            "destination": "ACC123"
        }
        transaction = TransactionCreate(**data)
        
        assert transaction.type == "deposit"
        assert transaction.amount == 100.0
        assert transaction.destination == "ACC123"
        assert transaction.origin is None
    
    def test_transaction_create_withdraw_valid(self):
        """Test TransactionCreate pour un retrait valide"""
        data = {
            "type": "withdraw",
            "amount": 50.0,
            "origin": "ACC123"
        }
        transaction = TransactionCreate(**data)
        
        assert transaction.type == "withdraw"
        assert transaction.amount == 50.0
        assert transaction.origin == "ACC123"
        assert transaction.destination is None
    
    def test_transaction_create_transfer_valid(self):
        """Test TransactionCreate pour un transfert valide"""
        data = {
            "type": "transfer",
            "amount": 75.0,
            "origin": "ACC123",
            "destination": "ACC456"
        }
        transaction = TransactionCreate(**data)
        
        assert transaction.type == "transfer"
        assert transaction.amount == 75.0
        assert transaction.origin == "ACC123"
        assert transaction.destination == "ACC456"
    
    def test_transaction_create_invalid_type(self):
        """Test TransactionCreate avec type invalide"""
        data = {
            "type": "invalid_type",
            "amount": 100.0,
            "destination": "ACC123"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            TransactionCreate(**data)
        
        assert "type" in str(exc_info.value)
    
    def test_transaction_create_negative_amount(self):
        """Test TransactionCreate avec montant négatif"""
        data = {
            "type": "deposit",
            "amount": -50.0,
            "destination": "ACC123"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            TransactionCreate(**data)
        
        assert "amount" in str(exc_info.value)
    
    def test_transaction_response_deposit(self):
        """Test TransactionResponse pour un dépôt"""
        destination_account = AccountSchema(id="ACC123", balance=150.0, owner_id=1)
        
        data = {
            "type": "deposit",
            "destination": destination_account
        }
        response = TransactionResponse(**data)
        
        assert response.type == "deposit"
        assert response.destination.id == "ACC123"
        assert response.destination.balance == 150.0
        assert response.origin is None
    
    def test_transaction_response_transfer(self):
        """Test TransactionResponse pour un transfert"""
        origin_account = AccountSchema(id="ACC123", balance=50.0, owner_id=1)
        destination_account = AccountSchema(id="ACC456", balance=150.0, owner_id=2)
        
        data = {
            "type": "transfer",
            "origin": origin_account,
            "destination": destination_account
        }
        response = TransactionResponse(**data)
        
        assert response.type == "transfer"
        assert response.origin.id == "ACC123"
        assert response.origin.balance == 50.0
        assert response.destination.id == "ACC456"
        assert response.destination.balance == 150.0


class TestSchemasRelationships:
    """Tests pour les relations entre schémas"""
    
    def test_user_with_accounts_relationship(self):
        """Test la relation User avec AccountSchema"""
        # Créer des comptes
        account1 = AccountSchema(id="ACC001", balance=100.0, owner_id=1)
        account2 = AccountSchema(id="ACC002", balance=200.0, owner_id=1)
        
        # Créer un utilisateur (note: dans la réalité, cette relation serait gérée différemment)
        user_data = {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com"
        }
        user = User(**user_data)
        
        assert user.id == 1
        assert user.name == "John Doe"
    
    def test_transaction_complete_flow(self):
        """Test un flux complet de transaction"""
        # Créer les comptes
        origin_account = AccountSchema(id="ACC001", balance=100.0, owner_id=1)
        destination_account = AccountSchema(id="ACC002", balance=50.0, owner_id=2)
        
        # Créer la transaction
        transaction_data = {
            "type": "transfer",
            "amount": 25.0,
            "origin": "ACC001",
            "destination": "ACC002"
        }
        transaction_create = TransactionCreate(**transaction_data)
        
        # Simuler le traitement
        origin_account.balance -= 25.0
        destination_account.balance += 25.0
        
        # Créer la réponse
        response_data = {
            "type": "transfer",
            "origin": origin_account,
            "destination": destination_account
        }
        transaction_response = TransactionResponse(**response_data)
        
        # Vérifications
        assert transaction_create.type == "transfer"
        assert transaction_create.amount == 25.0
        assert transaction_response.origin.balance == 75.0
        assert transaction_response.destination.balance == 75.0


class TestEdgeCases:
    """Tests pour les cas limites"""
    
    def test_account_zero_balance(self):
        """Test Account avec solde zéro"""
        data = {
            "id": "ACC001",
            "balance": 0.0,
            "owner_id": 1
        }
        account = AccountSchema(**data)
        
        assert account.balance == 0.0
    
    def test_account_large_balance(self):
        """Test Account avec un solde très élevé"""
        data = {
            "id": "ACC001",
            "balance": 999999999.99,
            "owner_id": 1
        }
        account = AccountSchema(**data)
        
        assert account.balance == 999999999.99
    
    def test_transaction_large_amount(self):
        """Test Transaction avec un montant très élevé"""
        data = {
            "type": "deposit",
            "amount": 1000000.0,
            "destination": "ACC001"
        }
        transaction = TransactionCreate(**data)
        
        assert transaction.amount == 1000000.0
    
    def test_user_long_names(self):
        """Test User avec des noms longs"""
        data = {
            "name": "John Alexander Christopher Doe The Third",
            "email": "john.doe@example.com",
            "password": "secret"
        }
        user = UserCreate(**data)
        
        assert user.name == "John Alexander Christopher Doe The Third"
    
    def test_account_special_characters_id(self):
        """Test Account avec ID contenant des caractères spéciaux"""
        data = {
            "id": "ACC-001_SPECIAL",
            "balance": 100.0,
            "owner_id": 1
        }
        account = AccountSchema(**data)
        
        assert account.id == "ACC-001_SPECIAL"
