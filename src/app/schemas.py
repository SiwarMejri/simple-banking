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
    owner_id: int = Field(..., gt=0)  # ✅ Doit être requis
    
    class Config:
        from_attributes = True

# Transaction Schemas - CORRECTION CRITIQUE
class TransactionCreate(BaseModel):
    type: str
    amount: float = Field(..., gt=0)
    account_id: str  # ✅ Utiliser account_id au lieu de origin/destination

    @validator('type')
    def validate_type(cls, v):
        if v not in ['deposit', 'withdraw', 'transfer']:
            raise ValueError('Type must be deposit, withdraw, or transfer')
        return v

class TransactionResponse(BaseModel):
    type: str
    account_id: str  # ✅ Utiliser account_id
    status: str = "success"
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        from_attributes = True
