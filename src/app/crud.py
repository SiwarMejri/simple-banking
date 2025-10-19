# src/app/crud.py
from sqlalchemy.orm import Session
from src.app.models.user import User
from src.app.models.account import Account
from src.app.schemas import UserCreate, AccountCreate

# -------------------- USERS --------------------
def create_user(db: Session, user: UserCreate):
    db_user = User(
        name=user.name,
        email=user.email,
        password=user.password  # ici pour tests, pas hashé
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

# -------------------- ACCOUNTS --------------------
def create_account(db: Session, account: AccountCreate):
    db_account = Account(
        id=account.id,
        owner_id=account.user_id,  # mapping correct
        balance=0
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def get_account(db: Session, account_id: str):
    return db.query(Account).filter(Account.id == account_id).first()

def update_balance(db: Session, account: Account, amount: float):
    account.balance += amount
    db.commit()
    db.refresh(account)
    return account
