# src/app/transaction_utils.py
from fastapi import Response
from src.app.database import SessionLocal
from .transaction import Transaction

db = SessionLocal()

def process_deposit(transaction: dict, response: Response):
    destination = transaction.get("destination")
    amount = transaction.get("amount")

    # Vérifier si une transaction précédente existe pour ce destinataire
    previous_tx = db.query(Transaction).filter_by(destination=destination).all()
    current_balance = sum(tx.amount for tx in previous_tx if tx.type == "deposit") \
                      - sum(tx.amount for tx in previous_tx if tx.type == "withdraw")

    new_balance = current_balance + amount

    # Créer le nouvel enregistrement de transaction
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
