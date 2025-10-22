from sqlalchemy import inspect, text
from src.app.models.base import Base
from src.app.models.database import engine
from src.app.models.account import Account

# Dictionnaire pour stocker les comptes en mémoire (exemple)
accounts = {}

def reset_state():
    """Réinitialise complètement l'état mémoire et la base SQLite."""
    accounts.clear()

    # Supprime explicitement les index avant drop_all (évite les conflits persistants)
    with engine.begin() as conn:
        conn.execute(text("DROP INDEX IF EXISTS ix_users_id"))
        conn.execute(text("DROP INDEX IF EXISTS ix_accounts_id"))
        conn.execute(text("DROP INDEX IF EXISTS ix_transactions_id"))
        Base.metadata.drop_all(bind=conn)
        Base.metadata.create_all(bind=conn)

def create_or_update_account(account_id: str, amount: float):
    """Crée ou met à jour un compte en mémoire avec un montant."""
    if account_id in accounts:
        accounts[account_id].balance += amount
    else:
        accounts[account_id] = Account(id=account_id, balance=amount, owner_id=1)  # Valeur par défaut pour owner_id
    return accounts[account_id]

def get_account_balance(account_id: str):
    """Récupère le solde d'un compte en mémoire."""
    return accounts.get(account_id)

def withdraw_from_account(account_id: str, amount: float):
    """Retire un montant d'un compte en mémoire si le solde est suffisant."""
    if account_id in accounts and accounts[account_id].balance >= amount:
        accounts[account_id].balance -= amount
        return accounts[account_id]
    return None

def transfer_between_accounts(origin_id: str, dest_id: str, amount: float):
    """Transfère un montant entre deux comptes en mémoire si possible."""
    if origin_id in accounts and dest_id in accounts and accounts[origin_id].balance >= amount:
        accounts[origin_id].balance -= amount
        accounts[dest_id].balance += amount
        return accounts[origin_id], accounts[dest_id]
    return None, None

def process_transaction(db_session, data):
    """Traite une transaction (placeholder pour extension future)."""
    if not data or "from_account" not in data or "to_account" not in data:
        return {"status": "failed", "message": "Missing parameters"}
    # Logique simplifiée (à étendre selon les besoins)
    return {"status": "success"}
    
