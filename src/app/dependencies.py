# src/app/dependencies.py
import os
from auth import get_current_user  # ✅ ajout pour résoudre real_get_current_user

TESTING = os.environ.get("TESTING", "0") == "1"

def get_user_dep():
    if TESTING:
        return {"preferred_username": "testuser", "realm_access": {"roles": ["admin"]}}
    return get_current_user()
