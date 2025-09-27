from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship  # ← à importer
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    accounts = relationship("Account", back_populates="owner")  # ← ajoute cette ligne

