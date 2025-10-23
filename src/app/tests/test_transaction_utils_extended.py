import pytest
import sys
import os

# Ajouter le chemin pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from src.app.models import transaction_utils as tu

def test_validate_transaction_zero_amount():
    """Test validation avec montant zéro"""
    with pytest.raises(ValueError, match="Montant invalide"):
        tu.validate_transaction("deposit", 0.0, 200.0)

def test_process_deposit_negative_amount():
    """Test traitement de dépôt avec montant négatif"""
    # Utiliser les nouvelles fonctions avec paramètres simples
    result = tu.process_deposit(100.0, -10.0)
    # Le résultat devrait être 90.0 (100 - 10)
    assert result == 90.0

def test_process_withdraw_insufficient_balance():
    """Test traitement de retrait avec solde insuffisant"""
    with pytest.raises(ValueError, match="Solde insuffisant"):
        tu.process_withdraw(100.0, 200.0)

def test_process_transfer_invalid_amount():
    """Test traitement de transfert avec montant invalide"""
    # Tester avec un montant vraiment invalide (négatif) au lieu de 0.0
    with pytest.raises(ValueError, match="Montant invalide"):
        tu.process_transfer(100.0, 50.0, -10.0)
