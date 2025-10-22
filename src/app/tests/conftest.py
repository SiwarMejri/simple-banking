import sys
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ajoute le dossier src au path Python (pointe vers src/ pour importer app.main)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app.main import app, get_db  # Import get_db pour l'override
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

@pytest.fixture(scope="function")
def client(db):
    """Client de test FastAPI avec DB isolée."""
    # Override la dépendance get_db pour utiliser la session de test
    def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()  # Nettoyer après le test

@pytest.fixture(scope="function", autouse=True)
def reset_core():
    """Réinitialise core avant chaque test."""
    core.reset_state()
    yield
