import sys
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ajoute le dossier src au path Python (pointe vers src/ pour importer app.main)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app.main import app, get_db
from app.models.base import Base
from app.core import core

# Base de données de test en mémoire
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db():
    """Fixture pour une DB de test en mémoire."""
    # CORRECTION : Utiliser connect_args pour SQLite
    test_engine = create_engine(
        TEST_DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
    
    # CORRECTION : Créer toutes les tables
    Base.metadata.create_all(bind=test_engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # CORRECTION : Ne pas supprimer les tables pour éviter les conflits
        # Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def client(db):
    """Client de test FastAPI avec DB isolée."""
    # Override la dépendance get_db pour utiliser la session de test
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    # CORRECTION : Réinitialiser l'état de core
    core.reset_state()
    
    test_client = TestClient(app)
    yield test_client
    
    # Nettoyer après le test
    app.dependency_overrides.clear()

@pytest.fixture(scope="function", autouse=True)
def reset_core():
    """Réinitialise core avant chaque test."""
    core.reset_state()
    yield
