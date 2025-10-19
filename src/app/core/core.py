# src/app/core/core.py
from typing import Optional, Dict
from src.app.models.account import Account
from src.app.models.database import Base, engine

# ---------------- Stockage en mémoire ----------------
accounts: Dict[str, Account] = {}

def reset_state():
    """Réinitialise les comptes en mémoire et la base de données."""
    accounts.clear()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def get_account_balance(account_id: str) -> Optional[Account]:
    """Retourne un compte par son ID."""
    return accounts.get(account_id)

def create_or_update_account(account_id: str, amount: int) -> Account:
    """Crée un compte ou ajoute un montant à un compte existant."""
    if account_id in accounts:
        accounts[account_id].balance += amount
    else:
        accounts[account_id] = Account(id=account_id, balance=amount)
    return accounts[account_id]

def withdraw_from_account(account_id: str, amount: int) -> Optional[Account]:
    """Effectue un retrait."""
    if account_id not in accounts or accounts[account_id].balance < amount:
        return None
    accounts[account_id].balance -= amount
    return accounts[account_id]

def transfer_between_accounts(origin: str, destination: str, amount: int):
    """Transfert entre comptes."""
    if origin not in accounts or accounts[origin].balance < amount:
        return None, None
    accounts[origin].balance -= amount
    if destination not in accounts:
        accounts[destination] = Account(id=destination, balance=0)
    accounts[destination].balance += amount
    return accounts[origin], accounts[destination]

# ✅ Nouvelle fonction utilisée par les tests
def transfer_money(db, sender_account: Account, receiver_account: Account, amount: int):
    """Transfère de l'argent entre deux comptes en base."""
    if sender_account.balance < amount:
        raise ValueError("Solde insuffisant")
    sender_account.balance -= amount
    receiver_account.balance += amount
    db.commit()
    return True
