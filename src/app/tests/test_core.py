# tests/test_core.py
import pytest
from src.app.core.core import transfer_money, process_transaction
from src.app.crud import create_user, create_account
from src.app.schemas import UserCreate, AccountCreate

def test_transfer_money(db):
    user1 = create_user(db, UserCreate(name="A", email="a@test.com", password="123"))
    user2 = create_user(db, UserCreate(name="B", email="b@test.com", password="123"))
    acc1 = create_account(db, AccountCreate(id="acc1", user_id=user1.id))
    acc2 = create_account(db, AccountCreate(id="acc2", user_id=user2.id))

    # Ajouter de l'argent sur le compte 1
    acc1.balance = 500
    db.commit()

    # Transfert de 200
    transfer_money(db, acc1, acc2, 200)
    db.refresh(acc1)
    db.refresh(acc2)
    assert acc1.balance == 300
    assert acc2.balance == 200

    # Test transfert > solde
    with pytest.raises(ValueError):
        transfer_money(db, acc1, acc2, 400)
