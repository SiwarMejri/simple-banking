# src/app/core/core.py
from typing import Optional, Dict
from sqlalchemy import inspect, text
from src.app.models.account import Account
from src.app.models.database import Base, engine

# ---------------- Stockage en mémoire ----------------
accounts: Dict[str, Account] = {}

# ---------------- Réinitialisation ----------------
def reset_state():
    """Réinitialise les comptes en mémoire et la base de données."""
    accounts.clear()

    inspector = inspect(engine)

    # 🔥 Suppression sécurisée des indexes existants pour SQLite (SQLAlchemy 2.x)
    with engine.begin() as conn:
        for table_name in inspector.get_table_names():
            for idx in inspector.get_indexes(table_name):
                conn.execute(text(f"DROP INDEX IF EXISTS {idx['name']}"))

        # Réinitialisation complète des tables
        Base.metadata.drop_all(bind=conn)
        Base.metadata.create_all(bind=conn)

# ---------------- Fonctions principales ----------------
def get_account_balance(account_id: str) -> Optional[Account]:
    return accounts.get(account_id)

def create_or_update_account(account_id: str, amount: int) -> Account:
    if account_id in accounts:
        accounts[account_id].balance += amount
    else:
        accounts[account_id] = Account(id=account_id, balance=amount)
    return accounts[account_id]

def withdraw_from_account(account_id: str, amount: int) -> Optional[Account]:
    if account_id not in accounts or accounts[account_id].balance < amount:
        return None
    accounts[account_id].balance -= amount
    return accounts[account_id]

def transfer_between_accounts(origin: str, destination: str, amount: int):
    if origin not in accounts or accounts[origin].balance < amount:
        return None, None
    accounts[origin].balance -= amount
    if destination not in accounts:
        accounts[destination] = Account(id=destination, balance=0)
    accounts[destination].balance += amount
    return accounts[origin], accounts[destination]

# ---------------- Fonctions base de données ----------------
def transfer_money(db, sender_account: Account, receiver_account: Account, amount: int):
    if sender_account.balance < amount:
        raise ValueError("Solde insuffisant")
    sender_account.balance -= amount
    receiver_account.balance += amount
    db.commit()
    return True

def process_transaction(db, transaction_data: dict):
    try:
        from_account_id = transaction_data.get("from_account")
        to_account_id = transaction_data.get("to_account")
        amount = transaction_data.get("amount")

        if not all([from_account_id, to_account_id, amount]):
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
