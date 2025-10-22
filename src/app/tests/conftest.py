import sys
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ajoute le dossier src au path Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.app.main import app, get_db  # CORRECTION : Utiliser src.app.main
from src.app.models.base import Base
from src.app.core import core

# Base de données de test en mémoire
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db():
    """Fixture pour une DB de test en mémoire."""
    test_engine = create_engine(
        TEST_DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
    
    Base.metadata.create_all(bind=test_engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def client(db):
    """Client de test FastAPI avec DB isolée."""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    core.reset_state()
    
    test_client = TestClient(app)
    yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture(scope="function", autouse=True)
def reset_core():
    """Réinitialise core avant chaque test."""
    core.reset_state()
    yield
