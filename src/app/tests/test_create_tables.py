from models.base import Base
from models.database import engine
from create_tables import create_all_tables, get_inspector

def test_tables_created(db):  # Utilisation de la fixture db pour le moteur de test
    # db est le moteur de test (fixture modifiée)
    # Supprimer les tables si existantes
    Base.metadata.drop_all(bind=db)
    # Recréer
    Base.metadata.create_all(bind=db)  # Utilisation directe au lieu de create_all_tables pour le moteur de test
    # Vérifier que les tables existent
    inspector = get_inspector(db)  # Utilisation du moteur de test
    tables = inspector.get_table_names()
    assert "users" in tables
    assert "accounts" in tables
    assert "transactions" in tables
