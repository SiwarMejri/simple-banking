from sqlalchemy import Column, Integer, String
from ..database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    amount = Column(Integer)
    origin = Column(String, nullable=True)
    destination = Column(String, nullable=True)
