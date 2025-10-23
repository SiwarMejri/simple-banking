from sqlalchemy.orm import Session
from src.app.models import UserModel, AccountModel, TransactionModel
from schemas import UserCreate, AccountCreate

def get_user(db: Session, user_id: int):
    return db.query(UserModel).filter(UserModel.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(UserModel).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate):
    db_user = UserModel(name=user.name, email=user.email, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_account(db: Session, account_id: str):
    return db.query(AccountModel).filter(AccountModel.id == account_id).first()

def get_accounts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(AccountModel).offset(skip).limit(limit).all()

def create_account(db: Session, account: AccountCreate, user_id: int):
    db_account = AccountModel(id=account.id, balance=account.balance, owner_id=user_id)
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def get_transaction(db: Session, transaction_id: int):
    return db.query(TransactionModel).filter(TransactionModel.id == transaction_id).first()

def get_transactions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(TransactionModel).offset(skip).limit(limit).all()

def create_transaction(db: Session, transaction: dict):
    # CORRECTION : utiliser account_id au lieu de origin/destination
    db_transaction = TransactionModel(
        type=transaction.get("type"),
        amount=transaction.get("amount"),
        account_id=transaction.get("account_id")  # CORRECTION
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction
