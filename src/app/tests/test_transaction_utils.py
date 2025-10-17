# tests/test_transaction_utils.py
import pytest
from src.app.models.transaction_utils import calculate_fee, validate_transaction

def test_calculate_fee():
    assert calculate_fee(100) == 2  # si fee = 2%
    assert calculate_fee(0) == 0
    assert calculate_fee(1000) == 20

def test_validate_transaction():
    assert validate_transaction({"amount": 100, "balance": 200}) is True
    assert validate_transaction({"amount": 300, "balance": 200}) is False
    with pytest.raises(ValueError):
        validate_transaction({"amount": -50, "balance": 200})
