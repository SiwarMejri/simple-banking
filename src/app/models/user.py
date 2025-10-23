from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base

class UserModel(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    accounts = relationship("AccountModel", back_populates="owner")

# Alias pour les tests
User = UserModel
