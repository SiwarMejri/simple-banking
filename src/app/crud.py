from sqlalchemy.orm import Session
from src.app.models import User, Account, Transaction  # Import depuis __init__.py pour les alias
from src.app.schemas import UserCreate, AccountCreate

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate):
    db_user = User(name=user.name, email=user.email, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_account(db: Session, account_id: str):
    return db.query(Account).filter(Account.id == account_id).first()

def get_accounts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Account).offset(skip).limit(limit).all()

def create_account(db: Session, account: AccountCreate, user_id: int):
    db_account = Account(id=account.id, balance=account.balance, owner_id=user_id)
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def get_transaction(db: Session, transaction_id: int):
    return db.query(Transaction).filter(Transaction.id == transaction_id).first()

def get_transactions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Transaction).offset(skip).limit(limit).all()

def create_transaction(db: Session, transaction: dict):
    db_transaction = Transaction(
        type=transaction.get("type"),
        amount=transaction.get("amount"),
        origin=transaction.get("origin"),
        destination=transaction.get("destination")
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction
