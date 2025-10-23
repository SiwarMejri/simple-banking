from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class TransactionCreate(BaseModel):
    type: str
    amount: float = Field(..., gt=0)
    account_id: str  # ✅ CORRECTION : utiliser account_id au lieu de origin/destination

    @validator('type')
    def validate_type(cls, v):
        if v not in ['deposit', 'withdraw', 'transfer']:
            raise ValueError('Type must be deposit, withdraw, or transfer')
        return v

class TransactionResponse(BaseModel):
    type: str
    account_id: str  # ✅ CORRECTION : utiliser account_id
    status: str = "success"
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        from_attributes = True
