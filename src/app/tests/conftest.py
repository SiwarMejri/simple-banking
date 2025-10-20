# src/app/tests/conftest.py
import sys
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

# Ajout du chemin src pour les imports
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
    """Réinitialise complètement la base avant et après chaque test"""
    # Avant le test
    core.reset_state()
    yield
    # Après le test
    core.reset_state()
