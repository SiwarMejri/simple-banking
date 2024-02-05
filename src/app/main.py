from fastapi import FastAPI, status, Response
from .models import Transaction
from .core import core

app = FastAPI()

@app.post("/reset", status_code=status.HTTP_200_OK)
def reset_state():
    core.reset_state()
    return Response(content="OK", status_code=status.HTTP_200_OK)

@app.get("/balance")
def get_balance(account_id: str, response: Response):
    account = core.get_account_balance(account_id)
    if account is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return 0
    return account.balance

@app.post("/event", status_code=201)
def post_event(transaction: Transaction, response: Response):
    if transaction.type == "deposit":
        account = core.create_or_update_account(transaction.destination, transaction.amount)
        return {"destination": account}
    elif transaction.type == "withdraw":
        account = core.withdraw_from_account(transaction.origin, transaction.amount)
        if account is None:
            response.status_code = status.HTTP_404_NOT_FOUND
            return 0
        return {"origin": account}
    elif transaction.type == "transfer":
        origin, destination = core.transfer_between_accounts(transaction.origin, transaction.destination, transaction.amount)
        if origin is None:
            response.status_code = status.HTTP_404_NOT_FOUND
            return 0
        return {"origin": origin, "destination": destination}
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return response
