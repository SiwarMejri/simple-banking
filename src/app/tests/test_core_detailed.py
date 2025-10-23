import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from src.app.core.core import BankingCore

class TestCoreDetailed:
    """Tests détaillés pour core.py"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        self.core = BankingCore()
    
    def test_create_account_new(self):
        """Test création d'un nouveau compte"""
        account = self.core.create_account("ACC001", 100.0)
        assert account.id == "ACC001"
        assert account.balance == 100.0
    
    def test_create_account_existing(self):
        """Test création d'un compte existant - devrait retourner le compte existant"""
        account1 = self.core.create_account("ACC001", 100.0)
        account2 = self.core.create_account("ACC001", 200.0)
        # Le compte existant devrait être retourné, le solde ne change pas
        assert account2.balance == 100.0
        assert account1 is account2  # Même instance
    
    def test_get_account_exists(self):
        """Test récupération d'un compte existant"""
        self.core.create_account("ACC001", 100.0)
        account = self.core.get_account("ACC001")
        assert account is not None
        assert account.balance == 100.0
    
    def test_get_account_not_exists(self):
        """Test récupération d'un compte inexistant"""
        account = self.core.get_account("NONEXISTENT")
        assert account is None
    
    def test_withdraw_success(self):
        """Test retrait réussi"""
        self.core.create_account("ACC001", 100.0)
        account = self.core.withdraw("ACC001", 50.0)
        assert account is not None
        assert account.balance == 50.0
    
    def test_withdraw_insufficient_balance(self):
        """Test retrait avec solde insuffisant"""
        self.core.create_account("ACC001", 30.0)
        account = self.core.withdraw("ACC001", 50.0)
        assert account is None
    
    def test_withdraw_account_not_found(self):
        """Test retrait sur compte inexistant"""
        account = self.core.withdraw("NONEXISTENT", 50.0)
        assert account is None
    
    def test_deposit_success(self):
        """Test dépôt réussi"""
        self.core.create_account("ACC001", 100.0)
        account = self.core.deposit("ACC001", 50.0)
        assert account.balance == 150.0
    
    def test_deposit_account_not_found(self):
        """Test dépôt sur compte inexistant - devrait créer le compte"""
        account = self.core.deposit("NEW_ACCOUNT", 50.0)
        assert account is not None
        assert account.balance == 50.0
    
    def test_transfer_success(self):
        """Test transfert réussi"""
        self.core.create_account("ACC001", 100.0)
        self.core.create_account("ACC002", 50.0)
        
        result = self.core.transfer("ACC001", "ACC002", 30.0)
        assert result is True
        
        acc1 = self.core.get_account("ACC001")
        acc2 = self.core.get_account("ACC002")
        assert acc1.balance == 70.0
        assert acc2.balance == 80.0
    
    def test_transfer_insufficient_balance(self):
        """Test transfert avec solde insuffisant"""
        self.core.create_account("ACC001", 20.0)
        self.core.create_account("ACC002", 50.0)
        
        result = self.core.transfer("ACC001", "ACC002", 30.0)
        assert result is False
    
    def test_transfer_sender_not_found(self):
        """Test transfert avec expéditeur inexistant"""
        self.core.create_account("ACC002", 50.0)
        
        result = self.core.transfer("NONEXISTENT", "ACC002", 30.0)
        assert result is False
    
    def test_transfer_receiver_not_found(self):
        """Test transfert avec destinataire inexistant"""
        self.core.create_account("ACC001", 50.0)
        
        result = self.core.transfer("ACC001", "NONEXISTENT", 30.0)
        assert result is False
    
    def test_reset_state(self):
        """Test réinitialisation de l'état"""
        self.core.create_account("ACC001", 100.0)
        self.core.create_account("ACC002", 200.0)
        
        self.core.reset_state()
        
        assert len(self.core.accounts) == 0
        assert self.core.get_account("ACC001") is None
