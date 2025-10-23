from src.app.models.database import engine
from src.app.models.base import Base
from sqlalchemy import inspect
from src.app.models import user, account, transaction

def create_tables():
    """Crée toutes les tables dans la base de données."""
    Base.metadata.create_all(bind=engine)
    print("✅ Tables créées avec succès dans la base de données.")

def get_inspector(engine):
    """Fonction d'inspection pour les tests."""
    return inspect(engine)

def main():
    """Fonction principale pour créer les tables."""
    create_tables()
    print("✅ Tables créées avec succès!")
