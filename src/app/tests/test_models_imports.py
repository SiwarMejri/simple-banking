import pytest

class TestModelsImports:
    """Tests pour la structure des modèles"""
    
    def test_user_model_structure(self):
        """Test la structure du modèle User"""
        from src.app.models.user import UserModel
        
        assert UserModel is not None
        assert hasattr(UserModel, '__tablename__')
        assert UserModel.__tablename__ == 'users'
        
        # Vérifier les colonnes
        columns = [col.name for col in UserModel.__table__.columns]
        expected_columns = ['id', 'name', 'email', 'password']
        
        for col in expected_columns:
            assert col in columns, f"Column {col} should exist in UserModel"
    
    def test_account_model_structure(self):
        """Test la structure du modèle Account"""
        from src.app.models.account import AccountModel
        
        assert AccountModel is not None
        assert hasattr(AccountModel, '__tablename__')
        assert AccountModel.__tablename__ == 'accounts'
        
        # Vérifier les colonnes
        columns = [col.name for col in AccountModel.__table__.columns]
        expected_columns = ['id', 'balance', 'owner_id']
        
        for col in expected_columns:
            assert col in columns, f"Column {col} should exist in AccountModel"
    
    def test_transaction_model_structure(self):
        """Test la structure du modèle Transaction"""
        from src.app.models.transaction import TransactionModel
        
        assert TransactionModel is not None
        assert hasattr(TransactionModel, '__tablename__')
        assert TransactionModel.__tablename__ == 'transactions'
        
        # CORRECTION : Colonnes actuelles
        columns = [col.name for col in TransactionModel.__table__.columns]
        expected_columns = ['id', 'type', 'amount', 'account_id', 'created_at']  # account_id au lieu de origin/destination
        
        for col in expected_columns:
            assert col in columns, f"Column {col} should exist in TransactionModel"
    
    def test_models_relationships(self):
        """Test que les relations entre modèles sont définies"""
        from src.app.models.user import UserModel
        from src.app.models.account import AccountModel
        
        # Vérifier que UserModel a une relation accounts
        assert hasattr(UserModel, 'accounts')
        
        # Vérifier que AccountModel a une relation owner
        assert hasattr(AccountModel, 'owner')
