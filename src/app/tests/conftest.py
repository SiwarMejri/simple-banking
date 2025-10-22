import sys
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ajoute le dossier src au path Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from main import app  # Import direct depuis main.py pour éviter les conflits
from models.base import Base
from models.database import engine  # Ajout de l'import pour engine
from core import core

@pytest.fixture(scope="function")
def db():  # Modification : retourne le moteur de test au lieu de la session
    test_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    yield test_engine  # Retourne le moteur pour les tests qui en ont besoin
    session.close()
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="session")
def client():
    """Client de test FastAPI réutilisable pour toute la session."""
    return TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def reset_db():
    """Réinitialise complètement la base avant chaque test."""
    # Supprime et recréer la DB une seule fois ici (évite redondance avec core.reset_state)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
