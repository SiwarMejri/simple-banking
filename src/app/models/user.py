# src/app/models/user.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.app.models.database import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    # Relation vers Account
    accounts = relationship("Account", back_populates="owner")

    def __repr__(self):
        return f"<User(name='{self.name}', email='{self.email}')>"
