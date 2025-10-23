from sqlalchemy import Column, String, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field
from .base import Base

class AccountModel(Base):
    __tablename__ = "accounts"
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True, index=True)
    balance = Column(Float, default=0.0)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("UserModel", back_populates="accounts")
    transactions = relationship("TransactionModel", back_populates="account")

# AJOUTEZ CETTE LIGNE ↓
Account = AccountModel  # Alias pour les tests

class AccountBase(BaseModel):
    id: str
    balance: float = 0.0

class AccountCreate(AccountBase):
    user_id: int = Field(..., gt=0)

class AccountSchema(AccountBase):
    owner_id: int = Field(..., gt=0)
    
    class Config:
        from_attributes = True
