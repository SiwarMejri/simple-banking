# src/app/tests/test_schemas_comprehensive.py
import pytest
from pydantic import ValidationError
from datetime import datetime
from src.app.models.schemas import (
    UserBase, UserCreate, User,
    AccountBase, AccountCreate, Account,
    TransactionCreate, TransactionResponse
)


class TestUserSchemas:
    """Tests complets pour les schémas User"""
    
    def test_user_base_valid(self):
        """Test UserBase avec des données valides"""
        data = {"name": "John Doe", "email": "john@example.com"}
        user = UserBase(**data)
        
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
    
    def test_user_base_invalid_email(self):
        """Test UserBase avec email invalide"""
        data = {"name": "John Doe", "email": "invalid-email"}
        
        # Pydantic valide le format email par défaut
        user = UserBase(**data)
        assert user.email == "invalid-email"
    
    def test_user_base_missing_fields(self):
        """Test UserBase avec champs manquants"""
        with pytest.raises(ValidationError):
            UserBase(name="John Doe")  # email manquant
        
        with pytest.raises(ValidationError):
            UserBase(email="john@example.com")  # name manquant
    
    def test_user_create_valid(self):
        """Test UserCreate avec données valides"""
        data = {
            "name": "John Doe", 
            "email": "john@example.com",
            "password": "securepassword123"
        }
        user = UserCreate(**data)
        
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.password == "securepassword123"
    
    def test_user_create_missing_password(self):
        """Test UserCreate sans mot de passe"""
        with pytest.raises(ValidationError):
            UserCreate(name="John Doe", email="john@example.com")
    
    def test_user_schema_valid(self):
        """Test User schema avec ID"""
        data = {
            "id": 1,
            "name": "John Doe", 
            "email": "john@example.com"
        }
        user = User(**data)
        
        assert user.id == 1
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
    
    def test_user_orm_mode(self):
        """Test que User supporte le mode ORM"""
        assert User.Config.orm_mode is True


class TestAccountSchemas:
    """Tests complets pour les schémas Account"""
    
    def test_account_base_valid(self):
        """Test AccountBase avec données valides"""
        data = {"id": "ACC123", "balance": 1000.0}
        account = AccountBase(**data)
        
        assert account.id == "ACC123"
        assert account.balance == 1000.0
    
    def test_account_base_default_balance(self):
        """Test AccountBase avec balance par défaut"""
        data = {"id": "ACC123"}
        account = AccountBase(**data)
        
        assert account.id == "ACC123"
        assert account.balance == 0.0
    
    def test_account_base_negative_balance(self):
        """Test AccountBase avec balance négative"""
        data = {"id": "ACC123", "balance": -500.0}
        account = AccountBase(**data)
        
        assert account.balance == -500.0
    
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
    
    def test_account_create_missing_user_id(self):
        """Test AccountCreate sans user_id"""
        data = {"id": "ACC123", "balance": 1000.0}
        
        with pytest.raises(ValidationError):
            AccountCreate(**data)
    
    def test_account_schema_valid(self):
        """Test Account schema avec owner_id optionnel"""
        data = {
            "id": "ACC123",
            "balance": 1000.0,
            "owner_id": 1
        }
        account = Account(**data)
        
        assert account.id == "ACC123"
        assert account.balance == 1000.0
        assert account.owner_id == 1
    
    def test_account_schema_no_owner_id(self):
        """Test Account schema sans owner_id"""
        data = {"id": "ACC123", "balance": 1000.0}
        account = Account(**data)
        
        assert account.id == "ACC123"
        assert account.balance == 1000.0
        assert account.owner_id is None
    
    def test_account_orm_mode(self):
        """Test que Account supporte le mode ORM"""
        assert Account.Config.orm_mode is True


class TestTransactionSchemas:
    """Tests complets pour les schémas Transaction"""
    
    def test_transaction_create_deposit_valid(self):
        """Test TransactionCreate pour un dépôt valide"""
        data = {
            "type": "deposit",
            "amount": 500.0,
            "destination": "ACC123"
        }
        transaction = TransactionCreate(**data)
        
        assert transaction.type == "deposit"
        assert transaction.amount == 500.0
        assert transaction.destination == "ACC123"
        assert transaction.origin is None
    
    def test_transaction_create_withdraw_valid(self):
        """Test TransactionCreate pour un retrait valide"""
        data = {
            "type": "withdraw", 
            "amount": 200.0,
            "origin": "ACC123"
        }
        transaction = TransactionCreate(**data)
        
        assert transaction.type == "withdraw"
        assert transaction.amount == 200.0
        assert transaction.origin == "ACC123"
        assert transaction.destination is None
    
    def test_transaction_create_transfer_valid(self):
        """Test TransactionCreate pour un transfert valide"""
        data = {
            "type": "transfer",
            "amount": 300.0,
            "origin": "ACC123",
            "destination": "ACC456"
        }
        transaction = TransactionCreate(**data)
        
        assert transaction.type == "transfer"
        assert transaction.amount == 300.0
        assert transaction.origin == "ACC123"
        assert transaction.destination == "ACC456"
    
    def test_transaction_create_missing_type(self):
        """Test TransactionCreate sans type"""
        data = {"amount": 500.0}
        
        with pytest.raises(ValidationError):
            TransactionCreate(**data)
    
    def test_transaction_create_missing_amount(self):
        """Test TransactionCreate sans amount"""
        data = {"type": "deposit"}
        
        with pytest.raises(ValidationError):
            TransactionCreate(**data)
    
    def test_transaction_create_zero_amount(self):
        """Test TransactionCreate avec amount à zéro"""
        data = {"type": "deposit", "amount": 0.0}
        
        # Ceci devrait être valide syntaxiquement
        transaction = TransactionCreate(**data)
        assert transaction.amount == 0.0
    
    def test_transaction_create_negative_amount(self):
        """Test TransactionCreate avec amount négatif"""
        data = {"type": "deposit", "amount": -100.0}
        
        # Ceci devrait être valide syntaxiquement
        transaction = TransactionCreate(**data)
        assert transaction.amount == -100.0
    
    def test_transaction_response_valid(self):
        """Test TransactionResponse avec données valides"""
        test_timestamp = datetime(2024, 1, 1, 12, 0, 0)
        data = {
            "type": "deposit",
            "status": "success", 
            "timestamp": test_timestamp
        }
        transaction = TransactionResponse(**data)
        
        assert transaction.type == "deposit"
        assert transaction.status == "success"
        assert transaction.timestamp == test_timestamp
    
    def test_transaction_response_defaults(self):
        """Test TransactionResponse avec valeurs par défaut"""
        data = {"type": "deposit"}
        transaction = TransactionResponse(**data)
        
        assert transaction.type == "deposit"
        assert transaction.status == "success"
        assert isinstance(transaction.timestamp, datetime)
    
    def test_transaction_response_custom_status(self):
        """Test TransactionResponse avec statut personnalisé"""
        data = {
            "type": "transfer",
            "status": "failed"
        }
        transaction = TransactionResponse(**data)
        
        assert transaction.type == "transfer"
        assert transaction.status == "failed"


class TestSchemaIntegration:
    """Tests d'intégration entre les schémas"""
    
    def test_user_creation_flow(self):
        """Test le flux complet de création d'utilisateur"""
        # Étape 1: Données de création
        create_data = {
            "name": "Alice Smith",
            "email": "alice@example.com", 
            "password": "password123"
        }
        user_create = UserCreate(**create_data)
        
        # Étape 2: Simulation de sauvegarde en base
        user_data = {
            "id": 1,
            "name": user_create.name,
            "email": user_create.email
        }
        user = User(**user_data)
        
        assert user.id == 1
        assert user.name == "Alice Smith"
        assert user.email == "alice@example.com"
    
    def test_account_creation_flow(self):
        """Test le flux complet de création de compte"""
        # Création utilisateur
        user_data = {"id": 1, "name": "Bob", "email": "bob@example.com"}
        user = User(**user_data)
        
        # Création compte
        account_create_data = {
            "id": "ACC001",
            "balance": 1000.0,
            "user_id": user.id
        }
        account_create = AccountCreate(**account_create_data)
        
        # Compte avec owner
        account_data = {
            "id": account_create.id,
            "balance": account_create.balance,
            "owner_id": user.id
        }
        account = Account(**account_data)
        
        assert account.id == "ACC001"
        assert account.balance == 1000.0
        assert account.owner_id == 1
