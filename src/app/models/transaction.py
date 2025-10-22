from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class TransactionModel(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    amount = Column(Float)
    origin = Column(String, nullable=True)
    destination = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
