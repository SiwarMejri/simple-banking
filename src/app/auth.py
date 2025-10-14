# src/app/core/auth.py
# Auth simplifiée, sans Keycloak, Vault ni JWT

def get_current_user():
    """
    Bypass total de l'authentification.
    Mode test / dev : toujours retourne un utilisateur "admin".
    """
    return {"sub": "test-user", "preferred_username": "test_user", "roles": ["admin"]}
