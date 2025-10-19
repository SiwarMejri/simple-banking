# tests/test_create_tables.py
from sqlalchemy import inspect
from src.app import create_tables
from src.app.database import Base, engine

def test_tables_created():
    # 🔹 Supprimer les tables existantes
    Base.metadata.drop_all(bind=engine)
    # 🔹 Recréer les tables
    create_tables.create_all_tables()
    # 🔹 Vérifier la présence des tables
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    assert "users" in tables
    assert "accounts" in tables
    assert "transactions" in tables
