from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, List

# -------------------- USERS --------------------
class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    password: str

    # AJOUT : Validateur d'email pour que le test passe
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError('Invalid email format')
        return v

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

class AccountSchema(AccountBase):  # Renommé pour éviter conflit avec SQLAlchemy AccountModel
    owner_id: Optional[int] = None  # Rendu optionnel pour les tests
    class Config:
        orm_mode = True

# -------------------- TRANSACTIONS --------------------
class TransactionCreate(BaseModel):
    type: str
    amount: float
    origin: Optional[str] = None
    destination: Optional[str] = None

    @field_validator('type')
    @classmethod
    def type_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('type must not be empty')
        return v

    @field_validator('amount')
    @classmethod
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('amount must be positive')
        return v

class TransactionResponse(BaseModel):
    type: str
    status: Optional[str] = "success"
    timestamp: datetime = datetime.now()
    origin: Optional[AccountSchema] = None
    destination: Optional[AccountSchema] = None
