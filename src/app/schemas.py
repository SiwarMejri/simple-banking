from pydantic import BaseModel
from typing import List, Optional

# ----- Compte (on le met d'abord pour éviter les erreurs de type) -----
class Account(BaseModel):
    id: str
    balance: int

    model_config = {
        "from_attributes": True
    }


# ----- Utilisateur -----
class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    accounts: List[Account] = []

    model_config = {
        "from_attributes": True
    }


# ----- Compte Create (après User pour lier user_id) -----
class AccountCreate(BaseModel):
    id: str
    user_id: int


# ----- Transaction -----
class TransactionCreate(BaseModel):
    type: str
    origin: Optional[str] = None
    destination: Optional[str] = None
    amount: int

class TransactionResponse(BaseModel):
    type: str
    origin: Optional[Account] = None
    destination: Optional[Account] = None

    model_config = {
        "from_attributes": True
    }

