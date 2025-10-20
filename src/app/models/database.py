# src/app/models/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.app.models.base import Base
import os
import tempfile

# --- Choix du mode : test ou normal ---
TESTING = os.getenv("TESTING", "0") == "1"

if TESTING:
    # ⚡ Base temporaire (unique pour chaque test)
    tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    DATABASE_URL = f"sqlite:///{tmpfile.name}"
else:
    DATABASE_URL = "sqlite:///./banking.db"

# --- Création de l'engine ---
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
