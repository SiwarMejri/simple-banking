import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Récupération dynamique de l’URL de la base de données
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:admin@localhost/banking"  # Valeur par défaut si la variable n’est pas définie
)

# Création du moteur SQLAlchemy
engine = create_engine(DATABASE_URL, echo=True)  # echo=True pour debug SQL (optionnel)

# Création de la session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles ORM
Base = declarative_base()

# -----------------------------
# Fonction utilitaire pour FastAPI / tests
# -----------------------------
def get_db():
    """
    Fournit une session de base de données à utiliser dans les endpoints FastAPI.
    Utilisé avec Depends(get_db).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
