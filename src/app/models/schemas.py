# src/app/models/schemas.py

from pydantic import BaseModel
from typing import Optional
from sqlalchemy import Column, Integer, String
from models.database import Base  # ✅ Import corrigé

# --- Schéma Pydantic (utilisé pour FastAPI) ---
class TransactionSchema(BaseModel):
    type: str
    amount: int
    origin: Optional[str] = None
    destination: Optional[str] = None

    class Config:
        orm_mode = True  # ✅ Permet la compatibilité avec SQLAlchemy

# --- Modèle SQLAlchemy (pour la DB) ---
class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = {"extend_existing": True}  # ✅ Corrige le conflit de table

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    origin = Column(String, nullable=True)
    destination = Column(String, nullable=True)
