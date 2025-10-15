# tests/test_main.py
from fastapi.testclient import TestClient
from src.app.main import app

client = TestClient(app)

def test_root():
    """
    Vérifie que l'API FastAPI démarre correctement et répond sur la route /
    """
    response = client.get("/")
    assert response.status_code == 200
