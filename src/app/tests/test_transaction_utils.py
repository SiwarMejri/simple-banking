import pytest
from src.app.models.transaction_utils import calculate_fee, validate_transaction, process_deposit, process_withdraw, process_transfer

def test_calculate_fee():
    """Test calcul des frais à 5%"""
    assert calculate_fee(100) == 5.0
    assert calculate_fee(50) == 2.5

def test_validate_transaction_valid():
    """Test validation de transaction valide"""
    assert validate_transaction("deposit", 100.0, 200.0) is True
    assert validate_transaction("withdraw", 50.0, 100.0) is True

def test_validate_transaction_invalid_amount():
    """Test validation avec montant invalide"""
    with pytest.raises(ValueError, match="Montant invalide"):
        validate_transaction("deposit", -10.0, 200.0)

def test_validate_transaction_insufficient_balance():
    """Test validation avec solde insuffisant"""
    with pytest.raises(ValueError, match="Solde insuffisant"):
        validate_transaction("withdraw", 100.0, 50.0)

def test_process_deposit():
    """Test traitement de dépôt"""
    result = process_deposit(100.0, 50.0)
    assert result == 150.0

def test_process_withdraw():
    """Test traitement de retrait"""
    result = process_withdraw(100.0, 50.0)
    assert result == 50.0

def test_process_withdraw_insufficient():
    """Test traitement de retrait avec solde insuffisant"""
    with pytest.raises(ValueError, match="Solde insuffisant"):
        process_withdraw(30.0, 50.0)

def test_process_transfer():
    """Test traitement de transfert"""
    sender_balance, receiver_balance = process_transfer(100.0, 50.0, 30.0)
    # 100 - 30 - 1.5 (frais) = 68.5, 50 + 30 = 80
    assert sender_balance == 68.5
    assert receiver_balance == 80.0
