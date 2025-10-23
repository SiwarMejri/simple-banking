from pydantic import BaseModel, Field, validator
from typing import Optional, List
from enum import Enum
from datetime import datetime

class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    TRANSFER = "transfer"

class UserBase(BaseModel):
    name: str = Field(..., min_length=1)
    email: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=1)

class User(UserBase):  # Renommé de UserModel à User pour correspondre aux tests
    id: int
    accounts: List["AccountSchema"] = []

    class Config:
        from_attributes = True

class AccountBase(BaseModel):
    id: str
    balance: float = 0.0  # Valeur par défaut

class AccountCreate(AccountBase):
    user_id: int = Field(..., gt=0)

class AccountSchema(AccountBase):
    owner_id: int = Field(..., gt=0)

    class Config:
        from_attributes = True

class TransactionCreate(BaseModel):
    type: TransactionType
    amount: float = Field(..., gt=0)
    account_id: str  # CORRECTION : account_id au lieu de origin/destination

    @validator('type')
    def validate_type(cls, v):
        if v not in ['deposit', 'withdraw', 'transfer']:
            raise ValueError('Type must be deposit, withdraw, or transfer')
        return v

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        return v

class TransactionResponse(BaseModel):
    type: str
    account_id: str  # CORRECTION : account_id au lieu de origin/destination
    status: str = "success"
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True

# Mettre à jour les références
User.update_forward_refs()
