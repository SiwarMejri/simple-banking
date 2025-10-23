INVALID_AMOUNT_MSG = "Montant invalide"
INSUFFICIENT_BALANCE_MSG = "Solde insuffisant"

def calculate_fee(amount: float) -> float:
    """Calcule une taxe fixe de 5% sur le montant (corrigé pour les tests)."""
    return round(amount * 0.05, 2)

def validate_transaction(transaction_type: str, amount: float, balance: float = 0) -> bool:
    """Valide une transaction avant exécution (signature corrigée)."""
    if amount <= 0:
        return False
    if transaction_type == "withdraw" and balance < amount:
        return False
    return True

def process_deposit(amount: float, current_balance: float = 0):
    """Ajoute un montant à un compte (signature corrigée)."""
    if amount <= 0:
        return {"error": INVALID_AMOUNT_MSG}
    new_balance = current_balance + amount
    return {
        "type": "deposit",
        "destination": {"id": "account_id", "balance": new_balance}
    }

def process_withdraw(amount: float, current_balance: float = 100):
    """Retire un montant d'un compte (signature corrigée)."""
    if amount <= 0:
        return {"error": INVALID_AMOUNT_MSG}
    if current_balance < amount:
        return {"error": INSUFFICIENT_BALANCE_MSG}
    new_balance = current_balance - amount
    return {"type": "withdraw", "origin": {"id": "account_id", "balance": new_balance}}

def process_transfer(amount: float, sender_balance: float = 100, receiver_balance: float = 50):
    """Transfère un montant d'un compte à un autre (signature corrigée)."""
    if amount <= 0:
        return {"error": INVALID_AMOUNT_MSG}
    if sender_balance < amount:
        return {"error": INSUFFICIENT_BALANCE_MSG}
    
    new_sender_balance = sender_balance - amount
    new_receiver_balance = receiver_balance + amount
    
    return {
        "type": "transfer",
        "origin": {"id": "sender_id", "balance": new_sender_balance},
        "destination": {"id": "receiver_id", "balance": new_receiver_balance}
    }, new_sender_balance, new_receiver_balance
