import pytest
from sqlalchemy import inspect
from src.app.models.base import Base

def get_inspector(engine):
    return inspect(engine)

def test_tables_created(db):
    """Test que les tables sont créées correctement"""
    # Nettoyer et recréer les tables
    Base.metadata.drop_all(bind=db.bind)
    Base.metadata.create_all(bind=db.bind)
    
    # Vérifier que les tables existent
    inspector = get_inspector(db.bind)
    tables = inspector.get_table_names()
    
    # Vérifier les tables principales
    expected_tables = ["users", "accounts", "transactions"]
    for table in expected_tables:
        assert table in tables, f"Table {table} should exist"
