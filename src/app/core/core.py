# src/app/core/core.py
from sqlalchemy import inspect, text
from src.app.models.base import Base
from src.app.models.database import engine
from src.app.models.account import Account

# Dictionnaire pour stocker les comptes en mémoire
accounts = {}


def reset_state():
    """Réinitialise complètement l'état mémoire et la base SQLite."""
    accounts.clear()
    inspector = inspect(engine)

    with engine.begin() as conn:
        # Supprimer explicitement toutes les tables existantes
        for table_name in inspector.get_table_names():
            conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))

        # Supprimer tous les index restants
        for table_name in inspector.get_table_names():
            for idx in inspector.get_indexes(table_name):
                conn.execute(text(f"DROP INDEX IF EXISTS {idx['name']}"))

        # Recréer le schéma propre
        Base.metadata.create_all(bind=conn)


# ----------------------------------------------------------
# FONCTIONS MÉMOIRE
# ----------------------------------------------------------

def create_or_update_account(account_id: str, amount: float):
    """Crée un compte ou met à jour son solde."""
    if account_id not in accounts:
        accounts[account_id] = Account(id=account_id, balance=amount)
    else:
        accounts[account_id].balance += amount
    return accounts[account_id]


def withdraw_from_account(account_id: str, amount: float):
    """Retire un montant du compte si possible."""
    acc = accounts.get(account_id)
    if not acc:
        return None
    if acc.balance < amount:
        return None
    acc.balance -= amount
    return acc


def transfer_between_accounts(origin_id: str, dest_id: str, amount: float):
    """Transfère de l'argent entre deux comptes."""
    origin = accounts.get(origin_id)
    dest = accounts.get(dest_id)

    if not origin or not dest:
        return None, None
    if origin.balance < amount:
        return None, None

    origin.balance -= amount
    dest.balance += amount
    return origin, dest


# ----------------------------------------------------------
# FONCTIONS BASE DE DONNÉES
# ----------------------------------------------------------

def transfer_money(db, sender: Account, receiver: Account, amount: float):
    """
    Transfère de l'argent entre deux comptes (niveau base de données).
    Soulève ValueError si le solde est insuffisant.
    """
    if sender.balance < amount:
        raise ValueError("Solde insuffisant")

    sender.balance -= amount
    receiver.balance += amount
    db.add(sender)
    db.add(receiver)
    db.commit()
    return True


def process_transaction(db, data: dict):
    """
    Gère une transaction entre deux comptes.
    data = {"from_account": "a1", "to_account": "a2", "amount": 50}
    """
    from_id = data.get("from_account")
    to_id = data.get("to_account")
    amount = data.get("amount")

    sender = db.query(Account).filter(Account.id == from_id).first()
    receiver = db.query(Account).filter(Account.id == to_id).first()

    if not sender or not receiver:
        return {"status": "failed", "reason": "Un des comptes n'existe pas"}

    try:
        transfer_money(db, sender, receiver, amount)
        return {"status": "success", "from": from_id, "to": to_id, "amount": amount}
    except ValueError as e:
        return {"status": "failed", "reason": str(e)}
