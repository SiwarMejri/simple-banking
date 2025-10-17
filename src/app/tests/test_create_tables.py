# tests/test_create_tables.py
from src.app import create_tables
from src.app.database import engine, Base
import pytest

def test_tables_created():
    # Supprimer les tables si existantes
    Base.metadata.drop_all(bind=engine)
    # Recréer
    create_tables.create_all_tables()
    # Vérifier que les tables existent
    inspector = create_tables.inspect(engine)
    tables = inspector.get_table_names()
    assert "users" in tables
    assert "accounts" in tables
