# src/app/tests/conftest.py
import sys
import os
import pytest
from fastapi.testclient import TestClient

# Ajoute le dossier src au path Python pour que les imports fonctionnent
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app.main import app
from app.models.base import Base
from app.models.database import engine
from app.core import core

# ------------------ Client TestClient global ------------------
@pytest.fixture(scope="session")
def client():
    """
    Client de test FastAPI réutilisable pour toute la session.
    Utile pour éviter de recréer le client à chaque test.
    """
    return TestClient(app)

# ------------------ Fixture pour réinitialiser la base avant chaque test ------------------
@pytest.fixture(scope="function", autouse=True)
def reset_db():
    """
    Réinitialise complètement la base avant chaque test :
    - Supprime toutes les tables existantes
    - Recrée le schéma vide
    - Réinitialise l’état mémoire du module core
    """
    # Avant chaque test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    core.reset_state()

    yield  # Ici le test s'exécute

    # Après chaque test : nettoyage pour s'assurer qu'aucune donnée ne persiste
    Base.metadata.drop_all(bind=engine)
    core.reset_state()
