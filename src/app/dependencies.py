# src/app/dependencies.py
import os

TESTING = os.environ.get("TESTING", "0") == "1"

def get_user_dep():
    """
    Dépendance FastAPI pour récupérer l'utilisateur courant.
    En mode TESTING, renvoie un user factice.
    """
    if TESTING:
        return {"preferred_username": "testuser", "realm_access": {"roles": ["admin"]}}
    return real_get_current_user()
