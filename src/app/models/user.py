from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    # Relations - Correction des imports
    accounts = relationship("Account", back_populates="owner")
