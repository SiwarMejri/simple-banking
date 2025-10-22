# src/app/core/core.py
from typing import Optional, Dict, Tuple
from sqlalchemy.orm import Session
from src.app.models.base import Base
from src.app.models.database import engine
from src.app.models.account import Account
import os

# ---------------- Stockage en mémoire ----------------
accounts: Dict[str, Account] = {}

# ---------------- Réinitialisation ----------------
def reset_state():
    """
    Réinitialise les comptes en mémoire et la base de données SQLAlchemy.
    Pour SQLite, supprime le fichier DB si présent (tests ou dev).
    """
    accounts.clear()

    # Pour DB locale, supprimer le fichier
    db_file = "./banking.db"
    if os.path.exists(db_file):
        os.remove(db_file)

    # Recrée toutes les tables
    Base.metadata.create_all(bind=engine)

# ---------------- Fonctions principales (mémoire) ----------------
def get_account_balance(account_id: str) -> Optional[Account]:
    return accounts.get(account_id)

def create_or_update_account(account_id: str, amount: float) -> Account:
    if account_id in accounts:
        accounts[account_id].balance += amount
    else:
        accounts[account_id] = Account(id=account_id, balance=float(amount))
    return accounts[account_id]

def withdraw_from_account(account_id: str, amount: float) -> Optional[Account]:
    if account_id not in accounts or accounts[account_id].balance < amount:
        return None
    accounts[account_id].balance -= amount
    return accounts[account_id]

def transfer_between_accounts(origin: str, destination: str, amount: float) -> Tuple[Optional[Account], Optional[Account]]:
    if origin not in accounts or accounts[origin].balance < amount:
        return None, None
    accounts[origin].balance -= amount
    if destination not in accounts:
        accounts[destination] = Account(id=destination, balance=0.0)
    accounts[destination].balance += amount
    return accounts[origin], accounts[destination]

# ---------------- Fonctions base de données (DB via Session) ----------------
def transfer_money(db: Session, sender_account: Account, receiver_account: Account, amount: float) -> bool:
    if sender_account.balance < amount:
        raise ValueError("Solde insuffisant")
    sender_account.balance -= amount
    receiver_account.balance += amount
    try:
        db.commit()
    except Exception:
        pass
    return True

def process_transaction(db: Session, transaction_data: dict):
    try:
        from_account_id = transaction_data.get("from_account")
        to_account_id = transaction_data.get("to_account")
        amount = transaction_data.get("amount")

        if not all([from_account_id, to_account_id, amount is not None]):
            raise ValueError("Transaction invalide : paramètres manquants")

        sender = db.query(Account).filter(Account.id == from_account_id).first()
        receiver = db.query(Account).filter(Account.id == to_account_id).first()

        if not sender or not receiver:
            raise ValueError("Un des comptes n'existe pas")

        transfer_money(db, sender, receiver, amount)

        return {
            "status": "success",
            "from": sender.id,
            "to": receiver.id,
            "amount": amount
        }
    except Exception as e:
        return {"status": "failed", "reason": str(e)}
