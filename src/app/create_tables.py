# src/app/create_tables.py
from sqlalchemy import inspect
from src.app.database import Base, engine
from src.app.models.user import User
from src.app.models.account import Account
from src.app.models.transaction import Transaction


def create_all_tables():
    """Crée toutes les tables dans la base de données."""
    Base.metadata.create_all(bind=engine)
    print("✅ Tables créées avec succès dans la base de données.")


if __name__ == "__main__":
    create_all_tables()
    inspector = inspect(engine)
    print("📋 Tables présentes :", inspector.get_table_names())
