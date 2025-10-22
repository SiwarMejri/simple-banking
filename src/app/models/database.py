# src/app/models/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.app.models.base import Base
import os
import tempfile

# --- Choix du mode : test ou normal ---
TESTING = os.getenv("TESTING", "0") == "1"

if TESTING:
    # ⚡ Base en mémoire (DB volatile et propre à chaque session de test)
    DATABASE_URL = "sqlite:///:memory:"
else:
    DATABASE_URL = "sqlite:///./banking.db"

# --- Création de l'engine ---
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
