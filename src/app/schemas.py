from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    
    class Config:
        from_attributes = True

# Account Schemas
class AccountBase(BaseModel):
    id: str
    balance: float = 0.0

class AccountCreate(AccountBase):
    user_id: int = Field(..., gt=0)

class AccountSchema(AccountBase):
    owner_id: int = Field(..., gt=0)
    
    class Config:
        from_attributes = True

# Transaction Schemas - CORRIGÉ avec validation améliorée
class TransactionCreate(BaseModel):
    type: str
    amount: float = Field(..., gt=0)
    account_id: str  # Pour deposit/withdraw

    @validator('type')
def validate_type(cls, v):
    allowed_types = ['deposit', 'withdraw', 'transfer']
    if v not in allowed_types:
        # CORRECTION : Message exact attendu par le test
        raise ValueError('Type must be deposit, withdraw, or transfer')
    return v

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        return v

class TransactionResponse(BaseModel):
    type: str
    account_id: str
    status: str = "success"
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        from_attributes = True
