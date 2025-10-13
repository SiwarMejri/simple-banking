# src/app/core.py

from typing import Optional, Dict
from app.models.transaction_utils import Transaction, Account

# ---------------- Stockage en mémoire ----------------
accounts: Dict[str, Account] = {}

def reset_state():
    """Reset complet pour tests ou redémarrage"""
    accounts.clear()
    Transaction.transactions.clear()

def get_account_balance(account_id: str) -> Optional[Account]:
    """Retourne le compte existant ou None"""
    return accounts.get(account_id)

def create_or_update_account(account_id: str, amount: int) -> Account:
    """Crée un compte ou ajoute un montant si existant"""
    if account_id in accounts:
        accounts[account_id].balance += amount
    else:
        accounts[account_id] = Account(id=account_id, balance=amount)
    return accounts[account_id]

def withdraw_from_account(account_id: str, amount: int) -> Optional[Account]:
    """Retrait depuis un compte existant"""
    if account_id not in accounts or accounts[account_id].balance < amount:
        return None
    accounts[account_id].balance -= amount
    return accounts[account_id]

def transfer_between_accounts(origin: str, destination: str, amount: int) -> (Optional[Account], Optional[Account]):
    """Transfert entre comptes"""
    if origin not in accounts or accounts[origin].balance < amount:
        return None, None
    accounts[origin].balance -= amount
    if destination not in accounts:
        accounts[destination] = Account(id=destination, balance=0)
    accounts[destination].balance += amount
    return accounts[origin], accounts[destination]
