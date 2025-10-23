from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base  # CORRECTION : utiliser base locale

class TransactionModel(Base):
    __tablename__ = "transactions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    # CORRECTION : utiliser account_id au lieu de origin/destination
    account_id = Column(String, ForeignKey("accounts.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # CORRECTION : relation cohérente
    account = relationship("AccountModel", back_populates="transactions")
