# src/app/tests/conftest.py
import sys
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ajoute le dossier src au path Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app.main import app  # Import direct depuis main.py pour éviter les conflits
from app.models.base import Base
from app.models.database import engine  # Ajout de l'import pour engine
from app.core import core

@pytest.fixture(scope="function")
def db():
    """Fixture pour initialiser une base SQLite en mémoire avant chaque test."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

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
