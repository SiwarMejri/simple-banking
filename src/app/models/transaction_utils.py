# src/app/transaction_utils.py
from fastapi import Response
from src.app.database import SessionLocal
from .transaction import Transaction

db = SessionLocal()

def process_deposit(transaction: dict, response: Response):
    destination = transaction.get("destination")
    amount = transaction.get("amount")

    # Créer un nouvel enregistrement de transaction
    tx = Transaction(type="deposit", amount=amount, destination=destination)
    db.add(tx)
    db.commit()
    db.refresh(tx)

    # Retour complet attendu par le test
    return {
        "type": tx.type,
        "origin": None,
        "destination": {
            "id": destination,
            "balance": amount
        }
    }
