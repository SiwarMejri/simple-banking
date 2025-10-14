# src/app/tests/conftest.py
import sys
import os
import pytest
from fastapi.testclient import TestClient

# Ajoute le dossier src au path Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app.main import app
from app.dependencies import get_current_user

# ------------------ Mock global pour tous les tests ------------------
def fake_user():
    return {"username": "test_user"}

app.dependency_overrides[get_current_user] = fake_user

# ------------------ Client TestClient global ------------------
@pytest.fixture(scope="session")
def client():
    return TestClient(app)

# ------------------ Fixture pour reset DB avant chaque test ------------------
from app.models.base import Base
from app.models.database import engine
from app.core import core

@pytest.fixture(autouse=True)
def reset_db_before_test():
    """Réinitialise la base avant et après chaque test"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    core.reset_state()
    yield
    Base.metadata.drop_all(bind=engine)
    core.reset_state()
