from models.database import engine
from models.base import Base
from sqlalchemy import inspect  # Import pour l'inspection SQLAlchemy
from models import user, account, transaction  # Correction des imports : suppression de src.app

def create_all_tables():
    """Crée toutes les tables dans la base de données."""
    Base.metadata.create_all(bind=engine)
    print("✅ Tables créées avec succès dans la base de données.")

def get_inspector(engine):  # Renommage pour éviter la récursion
    """Fonction d'inspection pour les tests."""
    return inspect(engine)
