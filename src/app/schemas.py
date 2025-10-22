from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# -------------------- USERS --------------------
class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    class Config:
        orm_mode = True

# -------------------- ACCOUNTS --------------------
class AccountBase(BaseModel):
    id: str
    balance: float = 0

class AccountCreate(AccountBase):
    user_id: int

class AccountSchema(AccountBase):  # Renommé pour éviter conflit avec SQLAlchemy Account
    owner_id: Optional[int] = None  # Rendu optionnel pour les tests
    class Config:
        orm_mode = True

# -------------------- TRANSACTIONS --------------------
class TransactionCreate(BaseModel):
    type: str
    amount: float
    origin: Optional[str] = None
    destination: Optional[str] = None

class TransactionResponse(BaseModel):
    type: str
    status: Optional[str] = "success"
    timestamp: datetime = datetime.now()
    origin: Optional[AccountSchema] = None
    destination: Optional[AccountSchema] = None
