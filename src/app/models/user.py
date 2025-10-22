from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.app.database import Base

class UserModel(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}  # Ajoutez cette ligne

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # Ajouter cette colonne
    email = Column(String, unique=True, index=True)
    password = Column(String)

    # Relations
    accounts = relationship("AccountModel", back_populates="owner")
