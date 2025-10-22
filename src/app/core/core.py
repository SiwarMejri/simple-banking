from sqlalchemy import inspect, text
from src.app.models.base import Base
from src.app.models.database import engine

# Création d'une classe simple pour les comptes en mémoire (pas des modèles SQLAlchemy)
class MemoryAccount:
    def __init__(self, id: str, balance: float, owner_id: int = 1):
        self.id = id
        self.balance = balance
        self.owner_id = owner_id

# Dictionnaire pour stocker les comptes en mémoire
accounts = {}

def reset_state():
    """Réinitialise complètement l'état mémoire et la base SQLite."""
    accounts.clear()

    # Supprime explicitement les tables pour éviter les conflits persistants
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS transactions"))
        conn.execute(text("DROP TABLE IF EXISTS accounts"))
        conn.execute(text("DROP TABLE IF EXISTS users"))
        Base.metadata.create_all(bind=conn)

def create_or_update_account(account_id: str, amount: float):
    """Crée ou met à jour un compte en mémoire avec un montant."""
    if account_id in accounts:
        accounts[account_id].balance += amount
    else:
        accounts[account_id] = MemoryAccount(id=account_id, balance=amount, owner_id=1)
    return accounts[account_id]

def get_account_balance(account_id: str):
    """Récupère le solde d'un compte en mémoire."""
    account = accounts.get(account_id)
    return account.balance if account else None

def withdraw_from_account(account_id: str, amount: float):
    """Retire un montant d'un compte en mémoire si le solde est suffisant."""
    if account_id in accounts and accounts[account_id].balance >= amount:
        accounts[account_id].balance -= amount
        return accounts[account_id]
    return None

def transfer_between_accounts(origin_id: str, dest_id: str, amount: float):
    """Transfère un montant entre deux comptes en mémoire si possible."""
    if (origin_id in accounts and dest_id in accounts and 
        accounts[origin_id].balance >= amount):
        accounts[origin_id].balance -= amount
        accounts[dest_id].balance += amount
        return accounts[origin_id], accounts[dest_id]
    return None, None

def process_transaction(db_session, data):
    """Traite une transaction (placeholder pour extension future)."""
    if not data or "from_account" not in data or "to_account" not in data:
        return {"status": "failed", "message": "Missing parameters"}
    if "from_account" in data and data["from_account"] not in accounts:
        return {"status": "failed", "message": "From account not found"}
    if "to_account" in data and data["to_account"] not in accounts:
        return {"status": "failed", "message": "To account not found"}
    # Logique simplifiée (à étendre selon les besoins)
    return {"status": "success"}
