# src/app/core/core.py
from sqlalchemy import inspect, text
from src.app.models.base import Base
from src.app.models.database import engine
from src.app.models.account import Account

# Dictionnaire pour stocker les comptes en mémoire (exemple)
accounts = {}

def reset_state():
    """Réinitialise complètement l'état mémoire et la base SQLite."""
    accounts.clear()

    # Utilise SQLAlchemy pour supprimer et recréer tout proprement
    # Cela gère les tables, index, et évite les conflits (pas de suppression manuelle)
    with engine.begin() as conn:
        Base.metadata.drop_all(bind=conn)
        Base.metadata.create_all(bind=conn)

def create_or_update_account(account_id: str, amount: float):
    """Crée ou met à jour un compte en mémoire avec un montant initial."""
    if account_id in accounts:
        accounts[account_id].balance += amount
    else:
        accounts[account_id] = Account(id=account_id, balance=amount)
    return accounts[account_id]

def withdraw_from_account(account_id: str, amount: float):
    """Retire un montant d'un compte en mémoire."""
    if account_id not in accounts:
        return None
    account = accounts[account_id]
    if account.balance < amount:
        return None
    account.balance -= amount
    return account

def transfer_between_accounts(origin_id: str, dest_id: str, amount: float):
    """Transfère un montant entre deux comptes en mémoire."""
    if origin_id not in accounts or dest_id not in accounts:
        return None, None
    origin = accounts[origin_id]
    dest = accounts[dest_id]
    if origin.balance < amount:
        return None, None
    origin.balance -= amount
    dest.balance += amount
    return origin, dest

def get_account_balance(account_id: str):
    """Récupère le solde d'un compte en mémoire."""
    return accounts.get(account_id)
