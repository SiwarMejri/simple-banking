from fastapi import FastAPI, Request, Response, HTTPException, Depends, Form, Header
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from prometheus_client import Counter, REGISTRY
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
import logging
import os

from database import Base, engine, SessionLocal
from core import core
import crud
from models.user import User
from models.account import Account
from schemas import TransactionResponse, AccountCreate, Account as AccountSchema
from dependencies import get_current_user

# ---------------- Logging ----------------
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("fastapi-app")

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

# ---------------- Roles ----------------
ROLES_PERMISSIONS = {
    "admin": {"manage_users": True, "deploy_api": True, "read_metrics": True, "write_db": True},
    "developer": {"manage_users": False, "deploy_api": True, "read_metrics": True, "write_db": True},
    "auditor": {"manage_users": False, "deploy_api": False, "read_metrics": True, "write_db": False}
}

def require_permission(permission: str):
    def checker(user=Depends(get_current_user)):
        user_roles = user.get("realm_access", {}).get("roles", []) if user else []
        allowed = any(ROLES_PERMISSIONS.get(role, {}).get(permission, False) for role in user_roles)
        if not allowed:
            raise HTTPException(status_code=403, detail=f"Permission '{permission}' requise")
        return user
    return checker

# ---------------- Prometheus ----------------
def get_or_create_counter(name: str, description: str):
    if name in REGISTRY._names_to_collectors:
        return REGISTRY._names_to_collectors[name]
    return Counter(name, description)

user_created_counter = get_or_create_counter("user_created_total", "Nombre total d'utilisateurs créés")
api_reset_counter = get_or_create_counter("api_reset_total", "Nombre de resets de l'API")
transaction_processed_counter = get_or_create_counter("transaction_processed_total", "Nombre de transactions traitées")

instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

# ---------------- Endpoints ----------------
@app.get("/")
async def root():
    return {"message": "Hello, Simple Banking API!"}

@app.get("/protected")
async def protected(user=Depends(get_current_user)):
    return {"message": f"Hello {user.get('preferred_username','test-user')}, vous êtes authentifié"}

@app.get("/users/me")
def read_users_me(user=Depends(get_current_user)):
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
    return crud.create_account(db, account)

@app.get("/balance")
def get_balance(account_id: str, user=Depends(get_current_user)):
    account = core.get_account_balance(account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"account_id": account_id, "balance": account.balance}

@app.post("/reset", status_code=200)
def reset_state(user=Depends(require_permission("deploy_api"))):
    core.reset_state()
    api_reset_counter.inc()
    return {"message": "API reset executed"}

# ---------------- Transactions ----------------
class TransactionRequest(BaseModel):
    type: str
    origin: str | None = None
    destination: str | None = None
    amount: float

@app.post("/event", response_model=TransactionResponse)
async def process_transaction(transaction: TransactionRequest, user=Depends(get_current_user)):
    transaction_processed_counter.inc()
    if transaction.type == "deposit":
        account = core.create_or_update_account(transaction.destination, transaction.amount)
        return TransactionResponse(type="deposit", origin=None, destination=AccountSchema(id=account.id, balance=account.balance))
    elif transaction.type == "withdraw":
        account = core.withdraw_from_account(transaction.origin, transaction.amount)
        return TransactionResponse(type="withdraw", origin=AccountSchema(id=account.id, balance=account.balance), destination=None)
    elif transaction.type == "transfer":
        origin, destination = core.transfer_between_accounts(transaction.origin, transaction.destination, transaction.amount)
        return TransactionResponse(
            type="transfer",
            origin=AccountSchema(id=origin.id, balance=origin.balance) if origin else None,
            destination=AccountSchema(id=destination.id, balance=destination.balance) if destination else None
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid transaction type")

# ---------------- GitHub Webhook ----------------
@app.post("/github-webhook/")
async def github_webhook(request: Request):
    payload = await request.json()
    print(payload)
    return {"status": "received"}
