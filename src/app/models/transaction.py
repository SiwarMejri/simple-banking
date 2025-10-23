from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base

class TransactionModel(Base):
    __tablename__ = "transactions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    account_id = Column(String, ForeignKey("accounts.id"))  # ✅ Correct
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    account = relationship("AccountModel", back_populates="transactions")
