from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base  # ✅ Import unique

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}  # Évite l'erreur si redéclarée

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    accounts = relationship("Account", back_populates="owner")
