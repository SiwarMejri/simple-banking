# src/app/core/core.py
from sqlalchemy import inspect, text
from src.app.models.base import Base
from src.app.models.database import engine

# Dictionnaire pour stocker les comptes en mémoire (exemple)
accounts = {}


def reset_state():
    """Réinitialise complètement l'état mémoire et la base SQLite."""
    accounts.clear()

    inspector = inspect(engine)

    with engine.begin() as conn:
        # Supprimer explicitement toutes les tables existantes
        for table_name in inspector.get_table_names():
            conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))

        # Supprimer tous les index restants
        for table_name in inspector.get_table_names():
            for idx in inspector.get_indexes(table_name):
                conn.execute(text(f"DROP INDEX IF EXISTS {idx['name']}"))

        # Recréer le schéma propre
        Base.metadata.create_all(bind=conn)
