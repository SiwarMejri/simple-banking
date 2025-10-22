#src/app/tests/test_models_imports.py
import pytest
import inspect
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship


class TestModelsImports:
    """Tests corrigés pour les imports des modèles"""
    
    def test_user_model_structure(self):
        """Test la structure du modèle User"""
        from src.app.models.user import User
        
        assert User is not None
        assert hasattr(User, '__tablename__')
        assert User.__tablename__ == 'users'
        
        # Vérifier les colonnes
        columns = [col for col in User.__table__.columns]
        assert any(col.name == 'id' for col in columns)
        assert any(col.name == 'name' for col in columns)
        assert any(col.name == 'email' for col in columns)
    
    def test_account_model_structure(self):
        """Test la structure du modèle Account"""
        from src.app.models.account import Account
        
        assert Account is not None
        assert hasattr(Account, '__tablename__')
        assert Account.__tablename__ == 'accounts'
        
        columns = [col for col in Account.__table__.columns]
        assert any(col.name == 'id' for col in columns)
        assert any(col.name == 'balance' for col in columns)
        assert any(col.name == 'owner_id' for col in columns)
    
    def test_transaction_model_structure(self):
        """Test la structure du modèle Transaction"""
        from src.app.models.transaction import Transaction
        
        assert Transaction is not None
        assert hasattr(Transaction, '__tablename__')
        assert Transaction.__tablename__ == 'transactions'
        
        columns = [col for col in Transaction.__table__.columns]
        assert any(col.name == 'id' for col in columns)
        assert any(col.name == 'type' for col in columns)
        assert any(col.name == 'amount' for col in columns)
    
    def test_models_relationships(self):
        """Test que les relations entre modèles existent"""
        from src.app.models.user import User
        from src.app.models.account import Account
        
        # Vérifier que User a une relation accounts
        assert hasattr(User, 'accounts')
        
        # Vérifier que Account a une relation owner
        assert hasattr(Account, 'owner')
