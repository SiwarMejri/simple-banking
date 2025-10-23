from sqlalchemy import inspect, text
from src.app.models.base import Base
from src.app.models.database import engine

# Création d'une classe simple pour les comptes en mémoire (pas des modèles SQLAlchemy)
class MemoryAccount:
    def __init__(self, id: str, balance: float, owner_id: int = 1):
        self.id = id
        self.balance = balance
        self.owner_id = owner_id

# Dictionnaire pour stocker les comptes en mémoire
accounts = {}

def reset_state():
    """Réinitialise complètement l'état mémoire et la base SQLite."""
    accounts.clear()

    # Supprime explicitement les tables pour éviter les conflits persistants
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS transactions"))
        conn.execute(text("DROP TABLE IF EXISTS accounts"))
        conn.execute(text("DROP TABLE IF EXISTS users"))
        Base.metadata.create_all(bind=conn)

def create_or_update_account(account_id: str, amount: float):
    """Crée ou met à jour un compte en mémoire avec un montant."""
    if account_id in accounts:
        accounts[account_id].balance += amount
    else:
        accounts[account_id] = MemoryAccount(id=account_id, balance=amount, owner_id=1)
    return accounts[account_id]

def get_account_balance(account_id: str):
    """Récupère le solde d'un compte en mémoire."""
    account = accounts.get(account_id)
    return account.balance if account else None

def withdraw_from_account(account_id: str, amount: float):
    """Retire un montant d'un compte en mémoire si le solde est suffisant."""
    if account_id in accounts and accounts[account_id].balance >= amount:
        accounts[account_id].balance -= amount
        return accounts[account_id]
    return None

def transfer_between_accounts(origin_id: str, dest_id: str, amount: float):
    """Transfère un montant entre deux comptes en mémoire si possible."""
    if (origin_id in accounts and dest_id in accounts and 
        accounts[origin_id].balance >= amount):
        accounts[origin_id].balance -= amount
        accounts[dest_id].balance += amount
        return accounts[origin_id], accounts[dest_id]
    return None, None

def process_transaction(db_session, data):
    """Traite une transaction (placeholder pour extension future)."""
    if not data or "from_account" not in data or "to_account" not in data:
        return {"status": "failed", "message": "Missing parameters"}
    if "from_account" in data and data["from_account"] not in accounts:
        return {"status": "failed", "message": "From account not found"}
    if "to_account" in data and data["to_account"] not in accounts:
        return {"status": "failed", "message": "To account not found"}
    # Logique simplifiée (à étendre selon les besoins)
    return {"status": "success"}

# Ajoutez cette classe à la fin de votre fichier core.py
class BankingCore:
    """Classe principale pour les opérations bancaires."""
    
    def __init__(self):
        self.accounts = accounts  # Réutilise le dictionnaire existant
    
    def create_account(self, account_id: str, initial_balance: float = 0.0):
        """Crée un nouveau compte bancaire."""
        if account_id in self.accounts:
            raise ValueError(f"Le compte {account_id} existe déjà")
        
        self.accounts[account_id] = MemoryAccount(
            id=account_id, 
            balance=initial_balance, 
            owner_id=1
        )
        return self.accounts[account_id]
    
    def get_balance(self, account_id: str):
        """Récupère le solde d'un compte."""
        account = self.accounts.get(account_id)
        if not account:
            raise ValueError(f"Compte {account_id} non trouvé")
        return account.balance
    
    def deposit(self, account_id: str, amount: float):
        """Effectue un dépôt sur un compte."""
        return create_or_update_account(account_id, amount)
    
    def withdraw(self, account_id: str, amount: float):
        """Effectue un retrait sur un compte."""
        return withdraw_from_account(account_id, amount)
    
    def transfer(self, from_account: str, to_account: str, amount: float):
        """Effectue un transfert entre comptes."""
        return transfer_between_accounts(from_account, to_account, amount)

# Vous pouvez ajouter une instance globale si nécessaire
banking_core = BankingCore()
