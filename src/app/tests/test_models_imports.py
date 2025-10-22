import pytest
import inspect
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship


class TestModelsImports:
    """Tests corrigés pour les imports des modèles"""
    
    def test_user_model_structure(self):
        """Test la structure du modèle User"""
        from src.app.models.user import UserModel
        
        assert UserModel is not None
        assert hasattr(UserModel, '__tablename__')
        assert UserModel.__tablename__ == 'users'
        
        # Vérifier les colonnes
        columns = [col for col in UserModel.__table__.columns]
        assert any(col.name == 'id' for col in columns)
        assert any(col.name == 'name' for col in columns)
        assert any(col.name == 'email' for col in columns)
    
    def test_account_model_structure(self):
        """Test la structure du modèle Account"""
        from src.app.models.account import AccountModel
        
        assert AccountModel is not None
        assert hasattr(AccountModel, '__tablename__')
        assert AccountModel.__tablename__ == 'accounts'
        
        columns = [col for col in AccountModel.__table__.columns]
        assert any(col.name == 'id' for col in columns)
        assert any(col.name == 'balance' for col in columns)
        assert any(col.name == 'owner_id' for col in columns)
    
    def test_transaction_model_structure(self):
        """Test la structure du modèle Transaction"""
        from src.app.models.transaction import TransactionModel
        
        assert TransactionModel is not None
        assert hasattr(TransactionModel, '__tablename__')
        assert TransactionModel.__tablename__ == 'transactions'
        
        columns = [col for col in TransactionModel.__table__.columns]
        assert any(col.name == 'id' for col in columns)
        assert any(col.name == 'type' for col in columns)
        assert any(col.name == 'amount' for col in columns)
    
    def test_models_relationships(self):
        """Test que les relations entre modèles existent"""
        from src.app.models.user import UserModel
        from src.app.models.account import AccountModel
        
        # Vérifier que UserModel a une relation accounts
        assert hasattr(UserModel, 'accounts')
        
        # Vérifier que AccountModel a une relation owner
        assert hasattr(AccountModel, 'owner')
