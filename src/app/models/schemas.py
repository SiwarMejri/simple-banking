from pydantic import BaseModel, Field, validator
from typing import Optional, List
from enum import Enum

class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    TRANSFER = "transfer"

class UserBase(BaseModel):
    name: str = Field(..., min_length=1)
    email: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=1)

class UserModel(UserBase):
    id: int
    accounts: List["AccountSchema"] = []

    class Config:
        from_attributes = True

class AccountBase(BaseModel):
    id: str
    balance: float

class AccountCreate(AccountBase):
    user_id: int = Field(..., gt=0)  # Doit être > 0

class AccountSchema(AccountBase):
    owner_id: int = Field(..., gt=0)  # Doit être requis et > 0

    class Config:
        from_attributes = True

class TransactionCreate(BaseModel):
    type: TransactionType  # Utiliser l'Enum pour validation
    amount: float = Field(..., gt=0)  # Doit être > 0
    origin: Optional[str] = None
    destination: Optional[str] = None

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
    origin: Optional[AccountSchema] = None
    destination: Optional[AccountSchema] = None

# Mettre à jour les références
UserModel.update_forward_refs()
