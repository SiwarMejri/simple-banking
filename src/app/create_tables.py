from src.app.models.database import engine
from src.app.models.base import Base
from sqlalchemy import inspect  # Import pour l'inspection SQLAlchemy
# Importer les modèles pour s'assurer qu'ils sont enregistrés
from src.app.models import user, account, transaction

def create_all_tables():
    """Crée toutes les tables dans la base de données."""
    Base.metadata.create_all(bind=engine)
    print("✅ Tables créées avec succès dans la base de données.")

def get_inspector(engine):  # Renommage pour éviter la récursion
    """Fonction d'inspection pour les tests."""
    return inspect(engine)
