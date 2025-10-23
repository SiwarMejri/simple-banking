import pytest
from unittest.mock import MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from src.app.crud import get_user, get_users, create_user, get_account, get_accounts, create_account

class TestCrudDetailed:
    """Tests détaillés pour crud.py"""
    
    def test_get_user_found(self, db):
        """Test récupération d'un utilisateur existant"""
        from src.app.models.user import UserModel
        
        # Créer un utilisateur de test
        user = UserModel(name="Test User", email="test@example.com", password="password")
        db.add(user)
        db.commit()
        
        # Récupérer l'utilisateur
        result = get_user(db, user.id)
        assert result is not None
        assert result.name == "Test User"
    
    def test_get_user_not_found(self, db):
        """Test récupération d'un utilisateur inexistant"""
        result = get_user(db, 9999)  # ID qui n'existe pas
        assert result is None
    
    def test_get_users(self, db):
        """Test récupération de tous les utilisateurs"""
        from src.app.models.user import UserModel
        
        # Créer quelques utilisateurs
        user1 = UserModel(name="User 1", email="user1@example.com", password="pass")
        user2 = UserModel(name="User 2", email="user2@example.com", password="pass")
        db.add_all([user1, user2])
        db.commit()
        
        # Récupérer tous les utilisateurs
        users = get_users(db)
        assert len(users) >= 2
    
    def test_create_user(self, db):
        """Test création d'un utilisateur"""
        from src.app.schemas import UserCreate
        
        user_data = UserCreate(name="New User", email="new@example.com", password="password")
        user = create_user(db, user_data)
        
        assert user is not None
        assert user.name == "New User"
        assert user.email == "new@example.com"
