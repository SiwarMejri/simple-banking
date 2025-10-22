from models.base import Base
from models.database import engine
from create_tables import create_all_tables, get_inspector

def test_tables_created(db):  # Utilisation de la fixture db pour la session de test
    # db est une Session, utiliser db.bind pour l'Engine
    # Supprimer les tables si existantes
    Base.metadata.drop_all(bind=db.bind)
    # Recréer
    Base.metadata.create_all(bind=db.bind)  # Utilisation directe au lieu de create_all_tables pour le moteur de test
    # Vérifier que les tables existent
    inspector = get_inspector(db.bind)  # Utilisation de db.bind pour l'Engine
    tables = inspector.get_table_names()
    assert "users" in tables
    assert "accounts" in tables
    assert "transactions" in tables
