import pytest
from sqlalchemy import inspect
from src.app.models.base import Base

def get_inspector(engine):
    return inspect(engine)

def test_tables_created(db):
    """Test que les tables sont créées correctement"""
    # CORRECTION : Utiliser la connexion de la fixture db
    inspector = get_inspector(db.bind)
    tables = inspector.get_table_names()
    
    # Vérifier les tables principales
    expected_tables = ["users", "accounts", "transactions"]
    for table in expected_tables:
        assert table in tables, f"Table {table} should exist"
    
    # CORRECTION : Vérifier que les modèles fonctionnent
    from src.app.models.user import UserModel
    from src.app.models.account import AccountModel
    from src.app.models.transaction import TransactionModel
    
    # Test création d'instances
    user = UserModel(name="test", email="test@example.com", password="pass")
    db.add(user)
    db.commit()
    
    account = AccountModel(id="test-acc", balance=100.0, owner_id=user.id)
    db.add(account)
    db.commit()
    
    transaction = TransactionModel(type="deposit", amount=50.0, account_id="test-acc")
    db.add(transaction)
    db.commit()
    
    # Vérifier que les données sont persistées
    assert db.query(UserModel).count() == 1
    assert db.query(AccountModel).count() == 1
    assert db.query(TransactionModel).count() == 1
