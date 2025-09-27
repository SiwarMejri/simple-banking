# src/app/transaction_utils.py
from fastapi import Response
from src.app.database import SessionLocal
from .transaction import Transaction
from contextlib import contextmanager

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def process_deposit(transaction: dict, response: Response):
    destination = transaction.get("destination")
    amount = transaction.get("amount")

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
        "destination": {
            "id": destination,
            "balance": new_balance
        }
    }
    def process_withdraw(transaction: dict, response: Response):
    origin = transaction.get("origin")
    amount = transaction.get("amount")

    # Vérifier le solde actuel
    previous_tx = db.query(Transaction).filter_by(destination=origin).all()
    current_balance = sum(tx.amount for tx in previous_tx if tx.type == "deposit") \
                      - sum(tx.amount for tx in previous_tx if tx.type == "withdraw")

    if amount > current_balance:
        response.status_code = 403
        return {"error": "Solde insuffisant"}

    new_balance = current_balance - amount

    # Créer la transaction
    tx = Transaction(type="withdraw", amount=amount, destination=origin)
    db.add(tx)
    db.commit()
    db.refresh(tx)

    return {
        "type": tx.type,
        "origin": {"id": origin, "balance": new_balance},
        "destination": None
    }


def process_transfer(transaction: dict, response: Response):
    origin = transaction.get("origin")
    destination = transaction.get("destination")
    amount = transaction.get("amount")

    # Vérifier le solde de l'origine
    previous_tx = db.query(Transaction).filter_by(destination=origin).all()
    current_balance = sum(tx.amount for tx in previous_tx if tx.type == "deposit") \
                      - sum(tx.amount for tx in previous_tx if tx.type == "withdraw")

    if amount > current_balance:
        response.status_code = 403
        return {"error": "Solde insuffisant"}

    new_balance_origin = current_balance - amount

    # Créer la transaction de retrait pour l'origine
    tx_origin = Transaction(type="withdraw", amount=amount, destination=origin)
    db.add(tx_origin)

    # Créer la transaction de dépôt pour la destination
    tx_dest = Transaction(type="deposit", amount=amount, destination=destination)
    db.add(tx_dest)

    db.commit()
    db.refresh(tx_origin)
    db.refresh(tx_dest)

    # Calculer le nouveau solde pour la destination
    previous_tx_dest = db.query(Transaction).filter_by(destination=destination).all()
    new_balance_dest = sum(tx.amount for tx in previous_tx_dest if tx.type == "deposit") \
                       - sum(tx.amount for tx in previous_tx_dest if tx.type == "withdraw")

    return {
        "type": "transfer",
        "origin": {"id": origin, "balance": new_balance_origin},
        "destination": {"id": destination, "balance": new_balance_dest}
    }
