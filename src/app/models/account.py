from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class AccountModel(Base):
    __tablename__ = "accounts"

    id = Column(String, primary_key=True, index=True)
    balance = Column(Float, default=0.0)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    user = relationship("UserModel", back_populates="accounts")
