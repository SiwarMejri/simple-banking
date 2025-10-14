# src/app/models/user.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models.database import Base  # ✅ corrigé

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    accounts = relationship("Account", back_populates="owner")
