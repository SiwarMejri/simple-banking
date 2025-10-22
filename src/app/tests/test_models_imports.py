# src/app/tests/test_models_imports.py
import pytest
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship


class TestModelsImports:
    """Tests pour les imports des modèles"""
    
    def test_user_import(self):
        """Test l'import du modèle User"""
        from src.app.models.user import User
        
        assert User is not None
        assert hasattr(User, '__tablename__')
        assert User.__tablename__ == 'users'
    
    def test_account_import(self):
        """Test l'import du modèle Account"""
        from src.app.models.account import Account
        
        assert Account is not None
        assert hasattr(Account, '__tablename__')
        assert Account.__tablename__ == 'accounts'
    
    def test_transaction_import(self):
        """Test l'import du modèle Transaction"""
        from src.app.models.transaction import Transaction
        
        assert Transaction is not None
        assert hasattr(Transaction, '__tablename__')
        assert Transaction.__tablename__ == 'transactions'
    
    def test_models_have_correct_attributes(self):
        """Test que les modèles ont les attributs attendus"""
        from src.app.models.user import User
        from src.app.models.account import Account
        from src.app.models.transaction import Transaction
        
        # Vérifier User
        assert hasattr(User, 'id')
        assert hasattr(User, 'name')
        assert hasattr(User, 'email')
        assert hasattr(User, 'password')
        assert hasattr(User, 'accounts')
        
        # Vérifier Account
        assert hasattr(Account, 'id')
        assert hasattr(Account, 'balance')
        assert hasattr(Account, 'owner_id')
        assert hasattr(Account, 'owner')
        
        # Vérifier Transaction
        assert hasattr(Transaction, 'id')
        assert hasattr(Transaction, 'type')
        assert hasattr(Transaction, 'amount')
        assert hasattr(Transaction, 'origin')
        assert hasattr(Transaction, 'destination')
        assert hasattr(Transaction, 'timestamp')
    
    def test_relationships_exist(self):
        """Test que les relations entre modèles sont définies"""
        from src.app.models.user import User
        from src.app.models.account import Account
        
        # Vérifier la relation User -> Account
        user_relationship = getattr(User.accounts, 'property')
        assert user_relationship is not None
        
        # Vérifier la relation Account -> User
        account_relationship = getattr(Account.owner, 'property')
        assert account_relationship is not None
