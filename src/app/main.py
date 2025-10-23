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

from src.app.schemas import TransactionResponse, TransactionCreate, AccountCreate, AccountSchema
from src.app.models.database import SessionLocal, engine
from src.app.models.base import Base
from src.app.models.user import UserModel  # CORRECTION : Import direct du modèle User
from src.app.models.account import AccountModel
from src.app.models.transaction import TransactionModel
from src.app.core import core
from src.app import crud

# ---------------- Logging ----------------
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("fastapi-app")

# ---------------- FastAPI ----------------
app = FastAPI(title="Simple Banking API", version="1.0.0")
Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="src/app/templates")  # CORRECTION : Chemin correct
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
        # CORRECTION : Utiliser UserModel correctement
        new_user = UserModel(email=email, password=hashed_password, name=email.split('@')[0])  # Ajout du nom requis
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
    # CORRECTION : Utiliser la méthode core existante ou logique simplifiée
    if account_id in core.accounts:
        account = core.accounts[account_id]
        return {"account_id": account_id, "balance": account.balance}
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

    try:
        # CORRECTION : Utiliser account_id au lieu de origin/destination
        if transaction.type == "deposit":
            # Pour les dépôts, créer ou mettre à jour le compte
            account = core.create_or_update_account(transaction.account_id, transaction.amount)
            return TransactionResponse(
                type="deposit",
                account_id=account.id,
                status="success"
            )

        elif transaction.type == "withdraw":
            # Pour les retraits, vérifier si le compte existe
            if transaction.account_id not in core.accounts:
                raise HTTPException(status_code=404, detail="Account not found")
            
            account = core.withdraw_from_account(transaction.account_id, transaction.amount)
            if account:
                return TransactionResponse(
                    type="withdraw",
                    account_id=account.id,
                    status="success"
                )
            else:
                raise HTTPException(status_code=403, detail="Insufficient balance")

        elif transaction.type == "transfer":
            # CORRECTION : Les transferts nécessitent deux comptes - désactivés temporairement
            # car le schéma TransactionCreate n'a qu'un account_id
            raise HTTPException(
                status_code=400, 
                detail="Transfer functionality requires two accounts. Current schema only supports single account operations."
            )

        else:
            raise HTTPException(status_code=400, detail="Invalid transaction type")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing transaction: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ---------------- GitHub Webhook ----------------
@app.post("/github-webhook/")
async def github_webhook(request: Request):
    try:
        payload = await request.json()
        logger.info(f"Received GitHub webhook: {payload}")
        return {"status": "received"}
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}
