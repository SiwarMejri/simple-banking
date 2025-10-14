# src/app/models/schemas.py

from pydantic import BaseModel
from typing import Optional
from sqlalchemy import Column, Integer, String
from models.database import Base  # Assure-toi que Base est bien défini dans database.py

# --- Schéma Pydantic (pour FastAPI) ---
class TransactionSchema(BaseModel):
    type: str
    amount: int
    origin: Optional[str] = None
    destination: Optional[str] = None

    class Config:
        orm_mode = True  # Permet la compatibilité avec SQLAlchemy

# --- Modèle SQLAlchemy (pour la DB) ---
class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = {"extend_existing": True}  # Evite les conflits si la table existe déjà

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(length=50), nullable=False)  # Ajout d'une longueur pour String
    amount = Column(Integer, nullable=False)
    origin = Column(String(length=100), nullable=True)
    destination = Column(String(length=100), nullable=True)
