from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from src.app.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)  # e.g., "deposit", "withdraw", "transfer"
    amount = Column(Float)
    account_id = Column(String, ForeignKey("accounts.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    account = relationship("Account", back_populates="transactions")
