from app.models.base import Base
from app.models.database import engine
from app import create_tables

def test_tables_created():
    # Supprimer les tables si existantes
    Base.metadata.drop_all(bind=engine)
    # Recréer
    create_tables.create_all_tables()
    # Vérifier que les tables existent
    inspector = create_tables.get_inspector(engine)  # Utilisation de la fonction renommée
    tables = inspector.get_table_names()
    assert "users" in tables
    assert "accounts" in tables
    assert "transactions" in tables
