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

# ---------------- Fixture pour la session de test ----------------
@pytest.fixture(scope="session")
def client():
    """Client FastAPI réutilisable pour toute la session."""
    return TestClient(app)

# ---------------- Fixture pour la base de données ----------------
@pytest.fixture(scope="function")
def db():
    """Initialise et nettoie la base avant/après chaque test."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

# ---------------- Fixture pour réinitialiser la base avant chaque test ----------------
@pytest.fixture(autouse=True)
def setup_test_db():
    """Active la base en mémoire et réinitialise avant chaque test."""
    os.environ["TESTING"] = "1"
    core.reset_state()
