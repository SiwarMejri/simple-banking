import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from src.app.models.transaction_utils import calculate_fee, validate_transaction, process_deposit, process_withdraw, process_transfer

class TestTransactionUtilsDetailed:
    """Tests détaillés pour transaction_utils.py"""
    
    def test_calculate_fee_standard(self):
        """Test calcul des frais standard"""
        fee = calculate_fee(100.0)
        assert fee == 5.0  # 5% de 100
    
    def test_calculate_fee_zero(self):
        """Test calcul des frais avec montant zéro"""
        fee = calculate_fee(0.0)
        assert fee == 0.0
    
    def test_calculate_fee_large_amount(self):
        """Test calcul des frais avec montant élevé"""
        fee = calculate_fee(10000.0)
        assert fee == 500.0
    
    def test_validate_transaction_valid(self):
        """Test validation de transaction valide"""
        result = validate_transaction("deposit", 100.0, 200.0)
        assert result is True
    
    def test_validate_transaction_invalid_amount(self):
        """Test validation avec montant invalide"""
        result = validate_transaction("deposit", 0.0, 200.0)
        assert result is False
    
    def test_validate_transaction_insufficient_balance(self):
        """Test validation avec solde insuffisant"""
        result = validate_transaction("withdraw", 100.0, 50.0)
        assert result is False
    
    def test_process_deposit_success(self):
        """Test traitement de dépôt réussi"""
        result = process_deposit(100.0, 50.0)
        assert result == 150.0
    
    def test_process_withdraw_success(self):
        """Test traitement de retrait réussi"""
        result = process_withdraw(100.0, 50.0)
        assert result == 50.0
    
    def test_process_withdraw_insufficient(self):
        """Test traitement de retrait avec solde insuffisant"""
        result = process_withdraw(30.0, 50.0)
        assert result is None
    
    def test_process_transfer_success(self):
        """Test traitement de transfert réussi"""
        sender_balance, receiver_balance = process_transfer(100.0, 50.0, 30.0)
        assert sender_balance == 65.0  # 100 - 30 - 5 (frais)
        assert receiver_balance == 80.0  # 50 + 30
    
    def test_process_transfer_insufficient(self):
        """Test traitement de transfert avec solde insuffisant"""
        result = process_transfer(30.0, 50.0, 30.0)
        assert result is None
