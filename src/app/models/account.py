from sqlalchemy import Column, String, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base  # CORRECTION : utiliser base locale

class AccountModel(Base):
    __tablename__ = "accounts"
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True, index=True)
    balance = Column(Float, default=0.0)
    owner_id = Column(Integer, ForeignKey("users.id"))

    # CORRECTION : utiliser les noms complets des modèles
    owner = relationship("UserModel", back_populates="accounts")
    transactions = relationship("TransactionModel", back_populates="account")  # CORRECTION : TransactionModel
