# src/app/tests/conftest.py
import sys
import os
import pytest
from fastapi.testclient import TestClient

# Ajoute le dossier src au path Python pour que les imports fonctionnent
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app.main import app
from app.models.base import Base
from app.models.database import SessionLocal, engine
from app.core import core

# ------------------ Base de données de test ------------------
@pytest.fixture(scope="function")
def db():
    """Fixture pour initialiser et nettoyer la base avant/après chaque test"""
    session = SessionLocal()
    yield session
    session.close()

# ------------------ Client TestClient global ------------------
@pytest.fixture(scope="session")
def client():
    """Client de test FastAPI réutilisable pour toute la session"""
    return TestClient(app)

# ------------------ Réinitialisation automatique avant chaque test ------------------
@pytest.fixture(scope="function", autouse=True)
def reset_db():
    """
    Réinitialise complètement la base avant chaque test :
    - Supprime toutes les tables existantes
    - Recrée le schéma vide
    - Réinitialise l’état mémoire du module core
    """
    # Avant chaque test
    core.reset_state()

    yield  # Exécution du test

    # Après chaque test : nettoyage complet
    core.reset_state()
