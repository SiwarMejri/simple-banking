INVALID_AMOUNT_MSG = "Montant invalide"
INSUFFICIENT_BALANCE_MSG = "Solde insuffisant"

def calculate_fee(amount: float) -> float:
    """Calcule une taxe fixe de 2% sur le montant."""
    return round(amount * 0.02, 2)

def validate_transaction(balance: float, amount: float) -> bool:
    """Valide une transaction avant exécution."""
    if amount <= 0:
        raise ValueError(INVALID_AMOUNT_MSG)
    if balance < amount:
        raise ValueError(INSUFFICIENT_BALANCE_MSG)
    return True

def process_deposit(transaction, response=None):
    """Ajoute un montant à un compte."""
    if transaction["amount"] <= 0:
        if response:
            response.status_code = 400
        return {"error": INVALID_AMOUNT_MSG}
    return {
        "type": "deposit",
        "destination": {"id": transaction["destination"], "balance": transaction["amount"]}
    }

def process_withdraw(transaction, response=None):
    """Retire un montant d’un compte simulé."""
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

def process_transfer(transaction, response=None):
    """Transfère un montant d’un compte à un autre."""
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
    return {
        "type": "transfer",
        "origin": {"id": transaction["origin"], "balance": balance_origin - amount},
        "destination": {"id": transaction["destination"], "balance": amount}
    }
