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

def process_deposit(transaction: dict, response: Response = None):
    """
    Traite un dépôt.
    transaction: dict contenant 'destination' et 'amount'
    """
    destination = transaction.get("destination")
    amount = transaction.get("amount")

    if amount is None or amount <= 0:
        if response:
            response.status_code = 400
            return {"error": "Montant invalide"}
        raise ValueError("Montant invalide")

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
    """
    Traite un retrait.
    transaction: dict contenant 'origin' et 'amount'
    """
    origin = transaction.get("origin")
    amount = transaction.get("amount")

    if amount is None or amount <= 0:
        if response:
            response.status_code = 400
            return {"error": "Montant invalide"}
        raise ValueError("Montant invalide")

    with get_db() as db:
        previous_tx = db.query(Transaction).filter_by(destination=origin).all()
        current_balance = sum(tx.amount for tx in previous_tx if tx.type == "deposit") \
                          - sum(tx.amount for tx in previous_tx if tx.type == "withdraw")

        if amount > current_balance:
            if response:
                response.status_code = 403
                return {"error": "Solde insuffisant"}
            raise ValueError("Solde insuffisant")

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
    """
    Traite un transfert entre deux comptes.
    transaction: dict contenant 'origin', 'destination', et 'amount'
    """
    origin = transaction.get("origin")
    destination = transaction.get("destination")
    amount = transaction.get("amount")

    if amount is None or amount <= 0:
        if response:
            response.status_code = 400
            return {"error": "Montant invalide"}
        raise ValueError("Montant invalide")

    with get_db() as db:
        # Vérifier le solde du compte d'origine
        previous_tx_origin = db.query(Transaction).filter_by(destination=origin).all()
        balance_origin = sum(tx.amount for tx in previous_tx_origin if tx.type == "deposit") \
                         - sum(tx.amount for tx in previous_tx_origin if tx.type == "withdraw")

        if amount > balance_origin:
            if response:
                response.status_code = 403
                return {"error": "Solde insuffisant"}
            raise ValueError("Solde insuffisant")

        # Créer les transactions
        tx_origin = Transaction(type="withdraw", amount=amount, destination=origin)
        tx_dest = Transaction(type="deposit", amount=amount, destination=destination)
        db.add(tx_origin)
        db.add(tx_dest)
        db.commit()
        db.refresh(tx_origin)
        db.refresh(tx_dest)

        # Calculer le nouveau solde pour chaque compte
        previous_tx_dest = db.query(Transaction).filter_by(destination=destination).all()
        new_balance_dest = sum(tx.amount for tx in previous_tx_dest if tx.type == "deposit") \
                           - sum(tx.amount for tx in previous_tx_dest if tx.type == "withdraw")
        new_balance_origin = balance_origin - amount

    return {
        "type": "transfer",
        "origin": {"id": origin, "balance": new_balance_origin},
        "destination": {"id": destination, "balance": new_balance_dest}
    }
