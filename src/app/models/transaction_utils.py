# src/app/models/transaction_utils.py

from fastapi import Response
from contextlib import contextmanager
from models.database import SessionLocal  # ✅ corrigé
from models.transaction import Transaction  # ✅ corrigé

# ✅ Définition des constantes pour éviter la répétition
INVALID_AMOUNT_MSG = "Montant invalide"
INSUFFICIENT_BALANCE_MSG = "Solde insuffisant"


@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def process_deposit(transaction: dict, response: Response = None):
    destination = transaction.get("destination")
    amount = transaction.get("amount")

    if amount is None or amount <= 0:
        if response:
            response.status_code = 400
            return {"error": INVALID_AMOUNT_MSG}
        raise ValueError(INVALID_AMOUNT_MSG)

    with get_db() as db:
        previous_tx = db.query(Transaction).filter_by(destination=destination).all()
        current_balance = sum(tx.amount for tx in previous_tx if tx.type == "deposit") \
                          - sum(tx.amount for tx in previous_tx if tx.type == "withdraw")
        new_balance = current_balance + amount

        tx = Transaction(type="deposit", amount=amount, destination=destination)
        db.add(tx)
        db.commit()
        db.refresh(tx)

    return {
        "type": tx.type,
        "origin": None,
        "destination": {"id": destination, "balance": new_balance}
    }


def process_withdraw(transaction: dict, response: Response = None):
    origin = transaction.get("origin")
    amount = transaction.get("amount")

    if amount is None or amount <= 0:
        if response:
            response.status_code = 400
            return {"error": INVALID_AMOUNT_MSG}
        raise ValueError(INVALID_AMOUNT_MSG)

    with get_db() as db:
        previous_tx = db.query(Transaction).filter_by(destination=origin).all()
        current_balance = sum(tx.amount for tx in previous_tx if tx.type == "deposit") \
                          - sum(tx.amount for tx in previous_tx if tx.type == "withdraw")

        if amount > current_balance:
            if response:
                response.status_code = 403
                return {"error": INSUFFICIENT_BALANCE_MSG}
            raise ValueError(INSUFFICIENT_BALANCE_MSG)

        new_balance = current_balance - amount
        tx = Transaction(type="withdraw", amount=amount, destination=origin)
        db.add(tx)
        db.commit()
        db.refresh(tx)

    return {
        "type": tx.type,
        "origin": {"id": origin, "balance": new_balance},
        "destination": None
    }


def process_transfer(transaction: dict, response: Response = None):
    origin = transaction.get("origin")
    destination = transaction.get("destination")
    amount = transaction.get("amount")

    if amount is None or amount <= 0:
        if response:
            response.status_code = 400
            return {"error": INVALID_AMOUNT_MSG}
        raise ValueError(INVALID_AMOUNT_MSG)

    with get_db() as db:
        previous_tx_origin = db.query(Transaction).filter_by(destination=origin).all()
        balance_origin = sum(tx.amount for tx in previous_tx_origin if tx.type == "deposit") \
                         - sum(tx.amount for tx in previous_tx_origin if tx.type == "withdraw")

        if amount > balance_origin:
            if response:
                response.status_code = 403
                return {"error": INSUFFICIENT_BALANCE_MSG}
            raise ValueError(INSUFFICIENT_BALANCE_MSG)

        tx_origin = Transaction(type="withdraw", amount=amount, destination=origin)
        tx_dest = Transaction(type="deposit", amount=amount, destination=destination)
        db.add(tx_origin)
        db.add(tx_dest)
        db.commit()
        db.refresh(tx_origin)
        db.refresh(tx_dest)

        previous_tx_dest = db.query(Transaction).filter_by(destination=destination).all()
        new_balance_dest = sum(tx.amount for tx in previous_tx_dest if tx.type == "deposit") \
                           - sum(tx.amount for tx in previous_tx_dest if tx.type == "withdraw")
        new_balance_origin = balance_origin - amount

    return {
        "type": "transfer",
        "origin": {"id": origin, "balance": new_balance_origin},
        "destination": {"id": destination, "balance": new_balance_dest}
    }
