# src/app/models/transaction.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from src.app.models.database import Base

class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    origin_account = Column(String, ForeignKey("accounts.id"), nullable=True)
    destination_account = Column(String, ForeignKey("accounts.id"), nullable=True)

    # Relations avec chaînes
    origin_acc = relationship("Account", foreign_keys=[origin_account], back_populates="outgoing_transactions")
    dest_acc = relationship("Account", foreign_keys=[destination_account], back_populates="incoming_transactions")

    def __repr__(self):
        return f"<Transaction(type='{self.type}', amount={self.amount})>"
