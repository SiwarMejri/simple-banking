# src/app/auth.py
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer
from jose import jwt
from jose.utils import base64url_decode
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import json

bearer_scheme = HTTPBearer()

KEYCLOAK_URL = "http://192.168.240.143:8080/realms/simple-banking-realm"
JWKS_URL = f"{KEYCLOAK_URL}/protocol/openid-connect/certs"
AUDIENCE = ["account", "api-rest-client"]

try:
    jwks = requests.get(JWKS_URL).json()
    jwks_keys = {key['kid']: key for key in jwks['keys']}
except Exception as e:
    raise RuntimeError(f"Impossible de récupérer les clés Keycloak: {str(e)}")

def jwk_to_public_key(jwk: dict):
    e = int.from_bytes(base64url_decode(jwk['e']), "big")
    n = int.from_bytes(base64url_decode(jwk['n']), "big")
    public_numbers = serialization.rsa.RSAPublicNumbers(e, n)
    return public_numbers.public_key(default_backend())

def get_current_user(token: str = Security(bearer_scheme)):
    try:
        header = jwt.get_unverified_header(token.credentials)
        key_jwk = jwks_keys.get(header['kid'])
        if not key_jwk:
            raise HTTPException(status_code=401, detail="Clé JWT non trouvée")

        public_key = jwk_to_public_key(key_jwk)
        payload = jwt.decode(
            token.credentials,
            public_key,
            algorithms=[header['alg']],
            audience=AUDIENCE
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except jwt.JWTClaimsError:
        raise HTTPException(status_code=401, detail="Audience ou claims invalides")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token invalide: {str(e)}")
