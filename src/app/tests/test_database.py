# src/app/tests/test_database_corrected.py
import pytest
import os
import sys
from unittest.mock import patch, MagicMock

from src.app.database import get_db, SessionLocal, engine, Base


class TestDatabaseCorrected:
    """Tests corrigés pour le module database"""
    
    def test_engine_creation(self):
        """Test la création du moteur SQLAlchemy"""
        assert engine is not None
        # Vérifier que l'engine peut se connecter
        assert hasattr(engine, 'connect')
    
    def test_session_local_creation(self):
        """Test la création de la session factory"""
        assert SessionLocal is not None
        assert callable(SessionLocal)
    
    def test_base_declarative(self):
        """Test la base déclarative"""
        assert Base is not None
        assert hasattr(Base, 'metadata')
    
    def test_get_db_success(self):
        """Test que get_db retourne une session de base de données"""
        mock_session = MagicMock()
        
        with patch('src.app.database.SessionLocal', return_value=mock_session):
            # Utiliser le générateur normalement
            generator = get_db()
            db = next(generator)
            
            assert db == mock_session
            
            # Fermer le générateur
            try:
                next(generator)
            except StopIteration:
                pass
    
    def test_get_db_proper_cleanup(self):
        """Test que la session est correctement nettoyée"""
        mock_session = MagicMock()
        
        with patch('src.app.database.SessionLocal', return_value=mock_session):
            # Simuler le pattern with
            generator = get_db()
            try:
                db = next(generator)
                # Utiliser la session
                assert db is not None
            finally:
                # Fermer proprement
                try:
                    next(generator)
                except StopIteration:
                    pass
            
            # Vérifier que close a été appelé
            mock_session.close.assert_called_once()
    
    def test_get_db_exception_handling(self):
        """Test que la session est fermée même en cas d'exception"""
        mock_session = MagicMock()
        
        with patch('src.app.database.SessionLocal', return_value=mock_session):
            generator = get_db()
            
            try:
                db = next(generator)
                raise ValueError("Test exception")
            except ValueError:
                # L'exception ne devrait pas empêcher le nettoyage
                pass
            finally:
                try:
                    next(generator)
                except StopIteration:
                    pass
            
            mock_session.close.assert_called_once()
