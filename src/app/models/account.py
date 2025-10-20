# src/app/models/account.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from src.app.database import Base


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True, index=True)
    balance = Column(Float, default=0.0)
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Relation vers User
    owner = relationship("User", back_populates="accounts")

    # Relation vers Transaction
    outgoing_transactions = relationship("Transaction", foreign_keys="[Transaction.origin_account]", back_populates="origin_acc")
    incoming_transactions = relationship("Transaction", foreign_keys="[Transaction.destination_account]", back_populates="dest_acc")

    def __repr__(self):
        return f"<Account(id='{self.id}', balance={self.balance})>"
