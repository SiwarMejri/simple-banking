from pydantic import BaseModel

class Account(BaseModel):
    id: str
    balance: int

class Transaction(BaseModel):
    type: str
    amount: int
    origin: str = None
    destination: str = None
