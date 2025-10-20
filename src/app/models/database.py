# src/app/models/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Détecte si on est en mode test
TESTING = os.environ.get("TESTING") == "1"

# Base de données en mémoire pour les tests, fichier normal sinon
DATABASE_URL = "sqlite:///:memory:" if TESTING else "sqlite:///./banking.db"

# Création de l'engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Session et base de modèles
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
