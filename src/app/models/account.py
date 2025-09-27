from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Account(Base):
    __tablename__ = "accounts"

    id = Column(String, primary_key=True, index=True)  # identifiant du compte
    balance = Column(Float, default=0.0)               # solde du compte

    user_id = Column(Integer, ForeignKey("users.id"))  # 🔗 clé étrangère vers User.id

    owner = relationship("User", back_populates="accounts")  # 🔄 relation ORM

