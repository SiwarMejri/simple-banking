# src/app/models/account.py

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from models.database import Base  # ✅ chemin corrigé

class Account(Base):
    __tablename__ = "accounts"

    id = Column(String, primary_key=True, index=True)  # Identifiant du compte
    balance = Column(Float, default=0.0)               # Solde du compte

    user_id = Column(Integer, ForeignKey("users.id"))  # 🔗 Clé étrangère vers User.id

    owner = relationship("User", back_populates="accounts")  # 🔄 Relation ORM
