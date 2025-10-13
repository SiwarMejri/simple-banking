# src/app/main.py

# ---------------- Tracing ----------------
from .tracer_setup import tracer  # ⚠️ Importer en premier

# ---------------- FastAPI / Autres imports ----------------
from fastapi import FastAPI, Request, status, Response, HTTPException, Form, Depends, Header, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2AuthorizationCodeBearer
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
import logging
from passlib.context import CryptContext
from influxdb_client import InfluxDBClient, Point
from prometheus_client import Counter
from prometheus_fastapi_instrumentator import Instrumentator
import os
import hvac
from jwt import PyJWTError, decode as jwt_decode
from jwt import PyJWKClient
from pydantic import BaseModel

# ---------------- Imports internes ----------------
from .schemas import TransactionResponse, AccountCreate, Account as AccountSchema
from .core import core
from .database import Base, engine, SessionLocal
from . import crud
from .models.user import User
from .models.account import Account
from .dependencies import get_user_dep  # ✅ nouvelle dépendance
from .models.transaction_utils import process_deposit, process_withdraw, process_transfer, Transaction

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
templates = Jinja2Templates(directory="src/templates")
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
KEYCLOAK_CLIENT_SECRET = None

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

# ---------------- Roles ----------------
ROLES_PERMISSIONS = {
    "admin": {"manage_users": True, "deploy_api": True, "read_metrics": True, "write_db": True},
    "developer": {"manage_users": False, "deploy_api": True, "read_metrics": True, "write_db": True},
    "auditor": {"manage_users": False, "deploy_api": False, "read_metrics": True, "write_db": False}
}

def require_permission(permission: str):
    def checker(user=Depends(get_user_dep)):
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

# ---------------- Swagger sécurisé ----------------
@app.get("/docs", include_in_schema=False)
def custom_swagger_ui_html():
    from fastapi.openapi.utils import get_openapi
    return get_swagger_ui_html(
        openapi_url="/openapi-roles.json",
        title="Banking API Docs",
        oauth2_redirect_url="/docs/oauth2-redirect",
        init_oauth={
            "clientId": "api-rest-client",
            "clientSecret": KEYCLOAK_CLIENT_SECRET,
            "usePkceWithAuthorizationCodeGrant": True,
            "scopes": "openid profile email",
        },
    )

@app.get("/openapi-roles.json", include_in_schema=False)
def openapi_roles(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        token_str = authorization.split(" ")[1]
        jwk_client = PyJWKClient(f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/certs")
        signing_key = jwk_client.get_signing_key_from_jwt(token_str).key
        jwt_decode(token_str, signing_key, algorithms=["RS256"], audience="api-rest-client", issuer=f"{KEYCLOAK_URL}/realms/{REALM}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token invalide: {str(e)}")
    from fastapi.openapi.utils import get_openapi
    return JSONResponse(get_openapi(title="Banking API", version="1.0.0", routes=app.routes))

# ---------------- Endpoints ----------------
@app.get("/")
async def root():
    with tracer.start_as_current_span("root_endpoint"):
        return {"message": "Hello, Simple Banking API!"}

@app.get("/protected")
async def protected(user=Depends(get_user_dep)):
    return {"message": f"Hello {user['preferred_username']}, vous êtes authentifié"}

# ---------------- User management ----------------
@app.get("/users/me")
def read_users_me(user=Depends(get_user_dep)):
    return {"user": user}

@app.get("/create_user", response_class=HTMLResponse)
async def create_user_form(request: Request, user=Depends(require_permission("manage_users"))):
    return templates.TemplateResponse("create_user.html", {"request": request})

@app.post("/create_user")
async def create_user(email: str = Form(...), password: str = Form(...), user=Depends(require_permission("manage_users"))):
    db = SessionLocal()
    try:
        hashed_password = get_password_hash(password)
        new_user = User(name=email.split("@")[0], email=email, hashed_password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        send_metric("api_server", "user_created", 1)
        user_created_counter.inc()
        return {"message": "Utilisateur créé ✅", "user_id": new_user.id, "email": new_user.email}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erreur lors de la création : {str(e)}")
    finally:
        db.close()

# ---------------- Accounts ----------------
@app.post("/accounts/", response_model=AccountSchema)
def create_account(account: AccountCreate, db: Session = Depends(get_db), user=Depends(require_permission("write_db"))):
    result = crud.create_account(db, account)
    return result

@app.get("/balance")
def get_balance(account_id: str, user=Depends(require_permission("read_metrics"))):
    account = core.get_account_balance(account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"account_id": account_id, "balance": account.balance}

@app.post("/reset", status_code=status.HTTP_200_OK)
def reset_state(user=Depends(require_permission("deploy_api"))):
    core.reset_state()
    send_metric("api_server", "api_reset", 1)
    api_reset_counter.inc()
    return {"message": "API reset executed"}

# ---------------- Transactions ----------------
class TransactionRequest(BaseModel):
    type: str  # "deposit", "withdraw", "transfer"
    origin: str | None = None
    destination: str | None = None
    amount: float

@app.post("/event", response_model=TransactionResponse)
async def process_transaction(transaction: TransactionRequest, response: Response, db: Session = Depends(get_db), user=Depends(require_permission("write_db"))):
    transaction_processed_counter.inc()
    if transaction.type == "deposit":
        account = core.create_or_update_account(transaction.destination, transaction.amount)
        if not account:
            response.status_code = 404
            return TransactionResponse(type="deposit", origin=None, destination=None)
        return TransactionResponse(type="deposit", origin=None, destination=AccountSchema(id=account.id, balance=account.balance))
    elif transaction.type == "withdraw":
        account = core.withdraw_from_account(transaction.origin, transaction.amount)
        if not account:
            response.status_code = 404
            return TransactionResponse(type="withdraw", origin=AccountSchema(id=transaction.origin, balance=0), destination=None)
        return TransactionResponse(type="withdraw", origin=AccountSchema(id=account.id, balance=account.balance), destination=None)
    elif transaction.type == "transfer":
        origin, destination = core.transfer_between_accounts(transaction.origin, transaction.destination, transaction.amount)
        if origin is None or destination is None:
            response.status_code = 404
        return TransactionResponse(
            type="transfer",
            origin=AccountSchema(id=origin.id, balance=origin.balance) if origin else AccountSchema(id=transaction.origin, balance=0),
            destination=AccountSchema(id=destination.id, balance=destination.balance) if destination else AccountSchema(id=transaction.destination, balance=0)
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid transaction type")

# ---------------- Keycloak secret ----------------
@app.get("/keycloak-secret")
def keycloak_secret(user=Depends(require_permission("manage_users"))):
    if KEYCLOAK_CLIENT_SECRET:
        return {"keycloak_client_secret": KEYCLOAK_CLIENT_SECRET}
    raise HTTPException(status_code=500, detail="Secret Keycloak non disponible depuis Vault")

# ---------------- GitHub Webhook ----------------
@app.post("/github-webhook/")
async def github_webhook(request: Request):
    payload = await request.json()
    print(payload)
    return {"status": "received"}
