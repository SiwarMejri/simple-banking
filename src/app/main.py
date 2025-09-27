# src/app/main.py

# ---------------- Tracing ----------------
from app.tracer_setup import tracer  # ⚠️ Importer en premier pour que le service soit correct

# ---------------- FastAPI / Autres imports ----------------
from .transaction_utils import process_deposit
from fastapi import FastAPI, Request, status, Response, HTTPException, Form, Depends, Body
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import logging
from passlib.context import CryptContext
from influxdb_client import InfluxDBClient, Point
from prometheus_client import Counter
from prometheus_fastapi_instrumentator import Instrumentator
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

def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)):
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

if VAULT_ROLE_ID and VAULT_SECRET_ID:
    try:
        auth_response = vault_client.auth.approle.login(
            role_id=VAULT_ROLE_ID,
            secret_id=VAULT_SECRET_ID
        )
        vault_client.token = auth_response['auth']['client_token']
        logger.info("Vault AppRole authentication successful ✅")
    except Exception as e:
        logger.error(f"Erreur Vault AppRole: {e}")
        vault_client = None
else:
    logger.warning("VAULT_ROLE_ID ou VAULT_SECRET_ID non définis, Vault non authentifié ❌")
    vault_client = None

def get_keycloak_secret():
    if vault_client is None:
        logger.warning("Vault non disponible, retour du secret Keycloak par défaut ou None")
        return None
    try:
        secret = vault_client.secrets.kv.v2.read_secret_version(path='keycloak')
        return secret['data']['data']['api-rest-client-secret']
    except Exception as e:
        logger.error(f"Erreur récupération secret Keycloak depuis Vault: {e}")
        return None

KEYCLOAK_CLIENT_SECRET = get_keycloak_secret()

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

# ---------------- Span de test au démarrage ----------------
@app.on_event("startup")
async def startup_event():
    with tracer.start_as_current_span("startup_span"):
        logger.info("FastAPI startup span créé ✅")

# ---------------- Endpoints génériques ----------------
@app.get("/")
async def root():
    with tracer.start_as_current_span("root_endpoint"):
        return {"message": "Hello, Simple Banking API!"}

@app.get("/protected")
async def protected(user=Depends(get_current_user)):
    with tracer.start_as_current_span("protected_endpoint") as span:
        span.set_attribute("user_id", user.get("preferred_username", "unknown"))
        return {"message": f"Hello {user['preferred_username']}, vous êtes authentifié"}

@app.get("/secure-endpoint")
def secure_endpoint(user=Depends(get_current_user)):
    with tracer.start_as_current_span("secure_endpoint") as span:
        span.set_attribute("user_id", user.get("preferred_username", "unknown"))
        return {"message": f"Hello {user['preferred_username']}"}

# ---------------- Users ----------------
@app.get("/create_user", response_class=HTMLResponse)
async def create_user_form(request: Request, user=Depends(require_permission("manage_users"))):
    with tracer.start_as_current_span("create_user_form_endpoint") as span:
        span.set_attribute("admin_user", user.get("preferred_username", "unknown"))
        return templates.TemplateResponse("create_user.html", {"request": request})

@app.post("/create_user")
async def create_user(email: str = Form(...), password: str = Form(...), user=Depends(require_permission("manage_users"))):
    with tracer.start_as_current_span("create_user_endpoint") as span:
        span.set_attribute("admin_user", user.get("preferred_username", "unknown"))
        db = SessionLocal()
        try:
            hashed_password = get_password_hash(password)
            new_user = User(name=email.split("@")[0], email=email, hashed_password=hashed_password)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            send_metric("api_server", "user_created", 1)
            user_created_counter.inc()
            span.set_attribute("new_user_id", new_user.id)
            return {"message": "Utilisateur créé ✅", "user_id": new_user.id, "email": new_user.email}
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Erreur lors de la création : {str(e)}")
        finally:
            db.close()

# ---------------- Accounts ----------------
@app.post("/accounts/", response_model=AccountSchema)
def create_account(account: AccountCreate, db: Session = Depends(get_db), user=Depends(require_permission("write_db"))):
    with tracer.start_as_current_span("create_account_endpoint") as span:
        span.set_attribute("account_owner", user.get("preferred_username", "unknown"))
        result = crud.create_account(db, account)
        span.set_attribute("account_id", result.id)
        return result

@app.get("/balance")
def get_balance(account_id: str, user=Depends(require_permission("read_metrics"))):
    with tracer.start_as_current_span("get_balance_endpoint") as span:
        span.set_attribute("account_id", account_id)
        span.set_attribute("user_id", user.get("preferred_username", "unknown"))
        account = core.get_account_balance(account_id)
        if account is None:
            raise HTTPException(status_code=404, detail="Account not found")
        span.set_attribute("balance", account.balance)
        return {"account_id": account_id, "balance": account.balance}

@app.post("/reset", status_code=status.HTTP_200_OK)
def reset_state(user=Depends(require_permission("deploy_api"))):
    with tracer.start_as_current_span("reset_api_endpoint") as span:
        span.set_attribute("admin_user", user.get("preferred_username", "unknown"))
        core.reset_state()
        send_metric("api_server", "api_reset", 1)
        api_reset_counter.inc()
        span.add_event("API reset executed")
        return {"message": "API reset executed"}

# ---------------- Transactions / Event ----------------
# On conserve toutes les fonctions process_deposit, process_withdraw, process_transfer
# Mais l'endpoint /event renvoie maintenant un 201 Created
@app.post("/event", status_code=status.HTTP_201_CREATED)
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

# ---------------- Keycloak Secret ----------------
@app.get("/keycloak-secret")
def keycloak_secret(user=Depends(require_permission("manage_users"))):
    with tracer.start_as_current_span("keycloak_secret_endpoint") as span:
        span.set_attribute("admin_user", user.get("preferred_username", "unknown"))
        if KEYCLOAK_CLIENT_SECRET:
            return {"keycloak_client_secret": KEYCLOAK_CLIENT_SECRET}
        raise HTTPException(status_code=500, detail="Secret Keycloak non disponible depuis Vault")

@app.get("/account/{user_id}")
async def get_account(user_id: str, user=Depends(require_permission("read_metrics"))):
    with tracer.start_as_current_span("get_account_operation") as span:
        span.set_attribute("user_id", user_id)
        return {"user_id": user_id, "balance": 1000}

# ---------------- GitHub Webhook ----------------
@app.post("/github-webhook/")
async def github_webhook(request: Request):
    payload = await request.json()
    logger.info(f"GitHub Webhook payload reçu: {payload}")
    return {"status": "received"}

# ---------------- End of main.py ----------------
