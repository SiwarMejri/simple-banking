# src/app/core/core.py
from typing import Optional, Dict
from src.app.models.account import Account
from src.app.models.database import Base, engine
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

# ---------------- Stockage en mémoire ----------------
accounts: Dict[str, Account] = {}

# ---------------- Réinitialisation ----------------
def reset_state():
    """Réinitialise les comptes en mémoire et la base de données."""
    accounts.clear()

    # ⚡ Pour éviter l'erreur SQLite "index already exists"
    if 'sqlite' in str(engine.url):
        with engine.connect() as conn:
            try:
                conn.execute(text('DROP INDEX IF EXISTS ix_users_id'))
                conn.commit()
            except OperationalError:
                pass  # Ignore si l'index n'existe pas encore

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

# ---------------- Fonctions principales ----------------
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
    """Effectue un retrait depuis un compte."""
    if account_id not in accounts or accounts[account_id].balance < amount:
        return None
    accounts[account_id].balance -= amount
    return accounts[account_id]

def transfer_between_accounts(origin: str, destination: str, amount: int):
    """Effectue un transfert entre deux comptes en mémoire."""
    if origin not in accounts or accounts[origin].balance < amount:
        return None, None

    accounts[origin].balance -= amount
    if destination not in accounts:
        accounts[destination] = Account(id=destination, balance=0)
    accounts[destination].balance += amount
    return accounts[origin], accounts[destination]

# ---------------- Fonctions utilisées en base de données ----------------
def transfer_money(db, sender_account: Account, receiver_account: Account, amount: int):
    """Transfère de l'argent entre deux comptes persistés en base."""
    if sender_account.balance < amount:
        raise ValueError("Solde insuffisant")
    sender_account.balance -= amount
    receiver_account.balance += amount
    db.commit()
    return True

# ---------------- Nouvelle fonction : process_transaction ----------------
def process_transaction(db, transaction_data: dict):
    """
    Traite une transaction générique :
    - Vérifie les champs requis
    - Appelle transfer_money()
    - Retourne un message de succès ou d'erreur
    """
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
