import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.app.models.models import User, Account, Transaction

class TestModelsDetailed:
    """Tests détaillés pour les modèles"""
    
    def test_models_import(self):
        """Test que les modèles s'importent correctement"""
        from src.app.models.models import User, Account, Transaction
        assert User is not None
        assert Account is not None  
        assert Transaction is not None
    
    def test_user_model_attributes(self):
        """Test les attributs du modèle User"""
        assert hasattr(User, '__tablename__')
        assert User.__tablename__ == 'users'
    
    def test_account_model_attributes(self):
        """Test les attributs du modèle Account"""
        assert hasattr(Account, '__tablename__')
        assert Account.__tablename__ == 'accounts'
    
    def test_transaction_model_attributes(self):
        """Test les attributs du modèle Transaction"""
        assert hasattr(Transaction, '__tablename__')
        assert Transaction.__tablename__ == 'transactions'
