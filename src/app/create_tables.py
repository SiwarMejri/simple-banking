# src/app/create_tables.py
from database import Base, engine  # ✅ corrigé
from models.models import User, Account, Transaction  # ✅ corrigé

Base.metadata.create_all(bind=engine)
print("✅ Tables créées avec succès dans la base 'banking'.")
