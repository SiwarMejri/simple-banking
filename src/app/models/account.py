from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True)
    balance = Column(Integer, default=0)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="accounts")
