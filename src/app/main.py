# src/app/main.py

# ---------------- Tracing ----------------
from app.tracer_setup import tracer  # ⚠️ Importer en premier

# ---------------- FastAPI / Autres imports ----------------
from fastapi import FastAPI, Request, status, Response, HTTPException, Form, Depends, Body
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from influxdb_client import InfluxDBClient, Point
from prometheus_client import Counter
from prometheus_fastapi_instrumentator import Instrumentator
import logging
import os
import hvac

# ---------------- JWT / Keycloak ----------------
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import PyJWTError, decode as jwt_decode
from jwt import PyJWKClient

KEYCLOAK_URL = "http://192.168.240.143:8080"
REALM = "simple-banking-realm"
JWKS_URL = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/certs"
ISSUER = f"{KEYCLOAK_URL}/realms/{REALM}"
AUDIENCE = "api-rest-client"

security = HTTPBearer()

# Flag pour tests (désactive auth JWT)
TESTING = os.environ.get("TESTING", "0") == "1"

def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)):
    if TESTING:
        # User factice pour tests
        return {"preferred_username": "testuser", "realm_access": {"roles": ["admin"]}}
    try:
        token_str = token.credentials
        jwk_client = PyJWKClient(JWKS_URL)
        signing_key = jwk_client.get_signing_key_from_jwt(token_str).key
        payload = jwt_decode(
            token_str,
            signing_key,
            algorithms=["RS256"],
            audience=AUDIENCE,
            issuer=ISSUER
        )
        return payload
    except PyJWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token invalide: {str(e)}")

# ---------------- Imports internes ----------------
from .schemas import TransactionCreate, TransactionResponse, AccountCreate, Account as AccountSchema
from .core import core
from .database import Base, engine, SessionLocal
from . import crud
from .models.user import User
from .models.transaction_utils import process_deposit, process_withdraw, process_transfer
from .models.transaction_utils import Transaction

# ---------------- Logging ----------------
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("fastapi-app")

# ---------------- Prometheus counters ----------------
user_created_counter = Counter("user_created_total", "Nombre total d'utilisateurs créés")
api_reset_counter = Counter("api_reset_total", "Nombre de resets de l'API")
transaction_processed_counter = Counter("transaction_processed_total", "Nombre de transactions traitées")

# ---------------- InfluxDB ----------------
influx_client = InfluxDBClient(url="http://localhost:8086", token="mytoken", org="monitoring")
write_api = influx_client.write_api()

def send_metric(host: str, metric_name: str, value: float):
    logger.info(f"Envoi métrique vers InfluxDB: host={host}, metric={metric_name}, value={value}")
    point = Point(metric_name).tag("host", host).field("value", value)
    write_api.write(bucket="metrics", org="monitoring", record=point)

# ---------------- FastAPI ----------------
app = FastAPI()
Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="src/app/templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- Vault ----------------
VAULT_ADDR = os.environ.get("VAULT_ADDR", "http://192.168.240.143:8200")
VAULT_ROLE_ID = os.environ.get("VAULT_ROLE_ID")
VAULT_SECRET_ID = os.environ.get("VAULT_SECRET_ID")

vault_client = hvac.Client(url=VAULT_ADDR)
KEYCLOAK_CLIENT_SECRET = None  # Bypass Vault pour tests

# ---------------- Rôles ----------------
ROLES_PERMISSIONS = {
    "admin": {"manage_users": True, "deploy_api": True, "read_metrics": True, "write_db": True},
    "developer": {"manage_users": False, "deploy_api": True, "read_metrics": True, "write_db": True},
    "auditor": {"manage_users": False, "deploy_api": False, "read_metrics": True, "write_db": False}
}

def require_permission(permission: str):
    def checker(user=Depends(get_current_user)):
        user_roles = user.get("realm_access", {}).get("roles", [])
        allowed = any(ROLES_PERMISSIONS.get(role, {}).get(permission, False) for role in user_roles)
        if not allowed:
            raise HTTPException(status_code=403, detail=f"Permission '{permission}' requise")
        return user
    return checker

# ---------------- Prometheus ----------------
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

# ---------------- Startup ----------------
@app.on_event("startup")
async def startup_event():
    with tracer.start_as_current_span("startup_span"):
        logger.info("FastAPI startup span créé ✅")

# ---------------- Login test ----------------
@app.post("/login")
def login_for_tests(username: str = Body(...), password: str = Body(...)):
    if username == "testuser" and password == "testpass":
        return {"access_token": "test-token"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

# ---------------- Endpoints ----------------
@app.get("/")
async def root():
    return {"message": "Hello, Simple Banking API!"}

@app.get("/balance")
def get_balance(account_id: str, user=Depends(get_current_user)):
    account = core.get_account_balance(account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"account_id": account_id, "balance": account.balance}

@app.post("/event")
def handle_event(transaction: dict = Body(...), response: Response = None):
    if response is None:
        response = Response()
    tx_type = transaction.get("type")
    if tx_type == "deposit":
        return process_deposit(transaction, response)
    elif tx_type == "withdraw":
        return process_withdraw(transaction, response)
    elif tx_type == "transfer":
        return process_transfer(transaction, response)
    else:
        raise HTTPException(status_code=400, detail="Type de transaction inconnu")

@app.post("/reset")
def reset_state():
    core.reset_state()
    return {"message": "API reset executed"}
