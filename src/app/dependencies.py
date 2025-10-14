# src/app/dependencies.py

def get_current_user():
    """
    Version simplifiée sans Keycloak, Vault, JWT ou OAuth2.
    Toutes les routes sont accessibles librement.
    """
    return {"sub": "anonymous", "preferred_username": "public_user", "realm_access": {"roles": ["admin"]}}
