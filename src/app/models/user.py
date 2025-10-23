from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base  # CORRECTION : utiliser base locale

class UserModel(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    # CORRECTION : relation cohérente
    accounts = relationship("AccountModel", back_populates="owner")

# Ajouter un alias pour compatibilité
User = UserModel  # <- ALIAS POUR LES TESTS
