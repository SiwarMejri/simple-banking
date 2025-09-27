# test_vault.py
import pytest
from unittest.mock import MagicMock, patch
import hvac

# Variables de test fictives
role_id = "fake-role-id"
secret_id = "fake-secret-id"
fake_token = "fake-token"

@pytest.fixture
def mock_hvac_client():
    """
    Fixture pour remplacer hvac.Client par un mock pendant les tests.
    """
    with patch("hvac.Client") as MockClient:
        client_instance = MockClient.return_value
        # Simule la méthode login de AppRole
        client_instance.auth.approle.login = MagicMock(return_value={"auth": {"client_token": fake_token}})
        yield client_instance

def test_approle_login(mock_hvac_client):
    """
    Test de connexion AppRole simulée à Vault.
    """
    client = hvac.Client(url="http://localhost:8200")  # L'URL n'a plus d'importance
    resp = client.auth.approle.login(role_id=role_id, secret_id=secret_id)
    
    # Vérifie que login a été appelé avec les bons paramètres
    client.auth.approle.login.assert_called_once_with(role_id=role_id, secret_id=secret_id)
    
    # Vérifie que le token simulé est retourné
    assert resp["auth"]["client_token"] == fake_token

    print("Connexion simulée à Vault réussie avec token:", resp["auth"]["client_token"])
