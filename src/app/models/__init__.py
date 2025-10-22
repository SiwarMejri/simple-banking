from .base import Base
from .user import UserModel
from .account import AccountModel
from .transaction import TransactionModel

# Créer des alias pour une utilisation simplifiée
User = UserModel
Account = AccountModel
Transaction = TransactionModel

__all__ = ["Base", "User", "Account", "Transaction", "UserModel", "AccountModel", "TransactionModel"]
