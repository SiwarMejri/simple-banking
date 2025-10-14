# src/app/crud.py
from sqlalchemy.orm import Session
from models.user import User  # ✅ corrigé
from models.account import Account  # ✅ corrigé
from models import schemas  # ✅ corrigé

# --------- USER CRUD ---------
def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = User(
        name=user.name,
        email=user.email,
        hashed_password=fake_hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

# --------- ACCOUNT CRUD ---------
def get_account(db: Session, account_id: str):
    return db.query(Account).filter(Account.id == account_id).first()

def create_account(db: Session, account: schemas.AccountCreate):
    db_account = Account(
        id=account.id,
        user_id=account.user_id,
        balance=0
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def update_balance(db: Session, account: Account, amount: int):
    account.balance += amount
    db.commit()
    db.refresh(account)
    return account
