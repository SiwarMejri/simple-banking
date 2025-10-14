# src/app/models/transaction.py

from sqlalchemy import Column, Integer, String
from models.database import Base  # ✅ corrigé

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    amount = Column(Integer)
    origin = Column(String, nullable=True)
    destination = Column(String, nullable=True)
