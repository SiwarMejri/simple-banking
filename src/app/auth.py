# src/app/core/auth.py
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    if os.getenv("TESTING") == "1":
        # Mode test → bypass auth
        return {"sub": "test-user", "realm_access": {"roles": ["admin"]}}
    # Sinon, ici tu peux mettre ta vérification Keycloak
    if token != "valid-token":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return {"sub": "real-user", "realm_access": {"roles": ["admin"]}}
