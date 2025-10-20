# src/app/tests/conftest.py
import os
import sys
import tempfile
import pytest
from fastapi.testclient import TestClient
import glob

# Ajoute src au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# ⚡ Active le mode test
os.environ["TESTING"] = "1"

from app.main import app
from app.models.base import Base
from app.models.database import SessionLocal, engine
from app.core import core


# ------------------ Nettoyage automatique des anciennes bases ------------------
def _cleanup_old_dbs():
    """Supprime tous les fichiers SQLite (.db) avant les tests"""
    db_files = glob.glob("**/*.db", recursive=True)
    for db_file in db_files:
        try:
            os.remove(db_file)
            print(f"🧹 Supprimé: {db_file}")
        except Exception as e:
            print(f"⚠️ Impossible de supprimer {db_file}: {e}")


# ------------------ Exécution avant la session de test ------------------
@pytest.fixture(scope="session", autouse=True)
def setup_environment():
    """Nettoyage global avant toute exécution de tests"""
    _cleanup_old_dbs()
    core.accounts.clear()
    yield
    _cleanup_old_dbs()
    core.accounts.clear()


# ------------------ Base de données temporaire pour chaque test ------------------
@pytest.fixture(scope="function")
def db():
    """Base temporaire isolée pour chaque test"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


# ------------------ Client FastAPI global ------------------
@pytest.fixture(scope="session")
def client():
    """Client FastAPI réutilisable pour tous les tests"""
    return TestClient(app)
