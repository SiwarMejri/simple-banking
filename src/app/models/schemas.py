# src/app/models/schemas.py
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

class Account(AccountBase):
    owner_id: Optional[int]
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
