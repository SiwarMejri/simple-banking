INVALID_AMOUNT_MSG = "Montant invalide"
INSUFFICIENT_BALANCE_MSG = "Solde insuffisant"

def calculate_fee(amount: float) -> float:
    """Calcule une taxe fixe de 2% sur le montant."""
    return round(amount * 0.02, 2)

def validate_transaction(transaction_type: str, amount: float, balance: float = 0) -> bool:
    """Valide une transaction avant exécution."""
    if amount <= 0:
        raise ValueError(INVALID_AMOUNT_MSG)
    if transaction_type == "withdraw" and balance < amount:
        raise ValueError(INSUFFICIENT_BALANCE_MSG)
    return True

def process_deposit(transaction: dict, response=None):
    """Ajoute un montant à un compte."""
    amount = transaction["amount"]
    if amount <= 0:
        if response:
            response.status_code = 400
        return {"error": INVALID_AMOUNT_MSG}
    return {
        "type": "deposit",
        "destination": {"id": transaction["destination"], "balance": amount}
    }

def process_withdraw(transaction: dict, response=None):
    """Retire un montant d'un compte."""
    balance = 100  # valeur simulée
    amount = transaction["amount"]
    if amount <= 0:
        if response:
            response.status_code = 400
        return {"error": INVALID_AMOUNT_MSG}
    if balance < amount:
        if response:
            response.status_code = 403
        return {"error": INSUFFICIENT_BALANCE_MSG}
    new_balance = balance - amount
    return {"type": "withdraw", "origin": {"id": transaction["origin"], "balance": new_balance}}

def process_transfer(transaction: dict, response=None):
    """Transfère un montant d'un compte à un autre."""
    amount = transaction["amount"]
    if amount <= 0:
        if response:
            response.status_code = 400
        return {"error": INVALID_AMOUNT_MSG}
    balance_origin = 100
    if balance_origin < amount:
        if response:
            response.status_code = 403
        return {"error": INSUFFICIENT_BALANCE_MSG}
    
    new_sender_balance = balance_origin - amount
    new_receiver_balance = amount
    
    return {
        "type": "transfer",
        "origin": {"id": transaction["origin"], "balance": new_sender_balance},
        "destination": {"id": transaction["destination"], "balance": new_receiver_balance}
    }
