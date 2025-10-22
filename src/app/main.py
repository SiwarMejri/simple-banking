from fastapi import FastAPI, Request, HTTPException, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from prometheus_client import Counter, REGISTRY
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
import logging
import os

from schemas import TransactionResponse, TransactionCreate, AccountCreate, AccountSchema
from models.database import SessionLocal, engine
from models.base import Base
from models import User, Account, Transaction  # Import corrigé via __init__.py
from core import core
import crud

# ---------------- Logging ----------------
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("fastapi-app")

# ---------------- FastAPI ----------------
app = FastAPI(title="Simple Banking API", version="1.0.0")
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

# ---------------- Prometheus ----------------
def get_or_create_counter(name: str, description: str):
    if name in REGISTRY._names_to_collectors:
        return REGISTRY._names_to_collectors[name]
    return Counter(name, description)

user_created_counter = get_or_create_counter("user_created_total", "Nombre total d'utilisateurs créés")
api_reset_counter = get_or_create_counter("api_reset_total", "Nombre de resets de l'API")
transaction_processed_counter = get_or_create_counter("transaction_processed_total", "Nombre de transactions traitées")

if os.getenv("TESTING", "0") != "1":
    Instrumentator().instrument(app).expose(app)

# ---------------- Endpoints ----------------
@app.get("/")
def root():
    return {"message": "Welcome to the Simple Banking API"}

@app.get("/protected")
def protected():
    return {"message": "Hello, endpoint accessible librement (auth supprimée)."}

@app.get("/users/me")
def read_users_me():
    return {"user": None}

@app.get("/create_user", response_class=HTMLResponse)
def create_user_form(request: Request):
    return templates.TemplateResponse("create_user.html", {"request": request})

@app.post("/create_user")
def create_user(email: str = Form(...), password: str = Form(...)):
    db = SessionLocal()
    try:
        hashed_password = get_password_hash(password)
        # CORRECTION : Utiliser User directement depuis models
        new_user = User(email=email, password=hashed_password)
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
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    return crud.create_account(db, account, user_id=account.user_id)

@app.get("/balance")
def get_balance(account_id: str):
    account = core.get_account_balance(account_id)
    if account is not None:
        return {"account_id": account_id, "balance": getattr(account, "balance", account)}
    else:
        raise HTTPException(status_code=404, detail="Account not found")

@app.post("/reset")
def reset_state():
    core.reset_state()
    api_reset_counter.inc()
    return {"message": "API reset executed"}

# ---------------- Transactions ----------------
@app.post("/event", response_model=TransactionResponse)
def process_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    transaction_processed_counter.inc()

    # Vérifier si les comptes existent UNIQUEMENT pour retrait et transfert (pas pour dépôt, qui crée le compte)
    if transaction.type == "withdraw":
        if transaction.origin not in core.accounts:
            raise HTTPException(status_code=404, detail="Account not found")
    elif transaction.type == "transfer":
        if transaction.origin not in core.accounts or transaction.destination not in core.accounts:
            raise HTTPException(status_code=404, detail="Account not found")

    # Logique des transactions
    if transaction.type == "deposit":
        account = core.create_or_update_account(transaction.destination, transaction.amount)
        return TransactionResponse(
            type="deposit",
            origin=None,
            destination=AccountSchema(id=account.id, balance=account.balance, owner_id=account.owner_id)
        )
    elif transaction.type == "withdraw":
        account = core.withdraw_from_account(transaction.origin, transaction.amount)
        if account:
            return TransactionResponse(
                type="withdraw",
                origin=AccountSchema(id=account.id, balance=account.balance, owner_id=account.owner_id),
                destination=None
            )
        else:
            raise HTTPException(status_code=403, detail="Insufficient balance")
    elif transaction.type == "transfer":
        origin, dest = core.transfer_between_accounts(transaction.origin, transaction.destination, transaction.amount)
        if origin and dest:
            return TransactionResponse(
                type="transfer",
                origin=AccountSchema(id=origin.id, balance=origin.balance, owner_id=origin.owner_id),
                destination=AccountSchema(id=dest.id, balance=dest.balance, owner_id=dest.owner_id)
            )
        else:
            raise HTTPException(status_code=403, detail="Transfer failed")
    else:
        raise HTTPException(status_code=400, detail="Invalid transaction type")

# ---------------- GitHub Webhook ----------------
@app.post("/github-webhook/")
async def github_webhook(request: Request):
    payload = await request.json()
    logger.info(f"Received GitHub webhook: {payload}")
    return {"status": "received"}
