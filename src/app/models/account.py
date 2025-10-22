from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from src.app.database import Base

class AccountModel(Base):
    __tablename__ = "accounts"
    __table_args__ = {'extend_existing': True}  # Ajoutez cette ligne

    id = Column(String, primary_key=True, index=True)
    balance = Column(Float, default=0.0)
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Relations
    owner = relationship("UserModel", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")
