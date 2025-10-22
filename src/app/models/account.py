from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from src.app.database import Base

class Account(Base):
    __tablename__ = "accounts"

    id = Column(String, primary_key=True, index=True)
    balance = Column(Float, default=0.0)
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Relations - Correction des imports
    owner = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")
