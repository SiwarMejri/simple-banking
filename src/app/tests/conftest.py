# src/app/tests/conftest.py
import os
import sys
import pytest
from fastapi.testclient import TestClient
from src.app.core import core

# Ajout du chemin src pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# ⚡ Active le mode test
os.environ["TESTING"] = "1"

from app.main import app
from app.models.database import SessionLocal

@pytest.fixture(scope="function")
def db():
    """Base temporaire isolée pour chaque test"""
    core.reset_state()  # Reset complet DB + comptes avant test
    session = SessionLocal()
    yield session
    session.close()
    core.reset_state()  # Reset complet après test

@pytest.fixture(scope="session")
def client():
    """Client FastAPI global pour toute la session"""
    return TestClient(app)

@pytest.fixture(autouse=True, scope="function")
def reset_env():
    """Reset complet des comptes en mémoire avant et après chaque test"""
    core.accounts.clear()
    yield
    core.accounts.clear()

