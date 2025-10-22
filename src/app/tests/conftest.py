import sys
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ajoute le dossier src au path Python (pointe vers src/ pour importer app.main)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app.main import app  # Correction : Import depuis app.main (main.py dans src/app/)
from app.models.base import Base
from app.models.database import engine  # Pour référence, mais on utilisera test_engine
from app.core import core

@pytest.fixture(scope="function")
def db():
    """Fixture pour une DB de test en mémoire."""
    test_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    yield session  # Retourne la session pour les tests
    session.close()
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="session")
def client():
    """Client de test FastAPI réutilisable."""
    return TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def reset_db():
    """Réinitialise la DB de test avant chaque test."""
    # Utilise test_engine pour isolation (au lieu de engine global)
    test_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    # Réinitialise aussi core si nécessaire
    core.reset_state()
    yield
    Base.metadata.drop_all(bind=test_engine)
