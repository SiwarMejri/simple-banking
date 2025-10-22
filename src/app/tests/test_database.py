# src/app/tests/test_database.py
import pytest
import os
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError

from src.app.database import get_db, SessionLocal, engine, Base, DATABASE_URL


class TestDatabase:
    """Tests pour le module database"""
    
    def test_database_url_from_env(self):
        """Test que DATABASE_URL est chargée depuis les variables d'environnement"""
        with patch.dict(os.environ, {'DATABASE_URL': 'sqlite:///test.db'}):
            # Reimport pour charger la nouvelle valeur
            import importlib
            import src.app.database
            importlib.reload(src.app.database)
            
            assert src.app.database.DATABASE_URL == 'sqlite:///test.db'
    
    def test_engine_creation(self):
        """Test la création du moteur SQLAlchemy"""
        assert engine is not None
        assert str(engine.url) == DATABASE_URL
    
    def test_session_local_creation(self):
        """Test la création de la session factory"""
        assert SessionLocal is not None
        assert hasattr(SessionLocal, '__call__')
    
    def test_base_declarative(self):
        """Test la base déclarative"""
        assert Base is not None
        assert hasattr(Base, 'metadata')
    
    def test_get_db_success(self):
        """Test que get_db retourne une session de base de données"""
        # Mock de la session
        mock_session = MagicMock()
        
        with patch('src.app.database.SessionLocal', return_value=mock_session):
            # Appel de la génératrice
            db_gen = get_db()
            db = next(db_gen)
            
            assert db == mock_session
            mock_session.close.assert_not_called()
    
    def test_get_db_finally_closes(self):
        """Test que la session est fermée dans le bloc finally"""
        mock_session = MagicMock()
        
        with patch('src.app.database.SessionLocal', return_value=mock_session):
            db_gen = get_db()
            
            # Consommer le générateur complètement
            try:
                next(db_gen)
            except StopIteration:
                pass
            
            # Vérifier que close a été appelé
            mock_session.close.assert_called_once()
    
    def test_get_db_with_exception(self):
        """Test que la session est fermée même en cas d'exception"""
        mock_session = MagicMock()
        
        with patch('src.app.database.SessionLocal', return_value=mock_session):
            db_gen = get_db()
            
            # Simuler une exception
            try:
                next(db_gen)
                raise ValueError("Test exception")
            except ValueError:
                pass
            finally:
                # S'assurer que le générateur est complètement consommé
                try:
                    next(db_gen)
                except StopIteration:
                    pass
            
            mock_session.close.assert_called_once()
    
    def test_database_url_default(self):
        """Test le comportement quand DATABASE_URL n'est pas définie"""
        with patch.dict(os.environ, clear=True):
            # Recharger le module pour simuler l'absence de variable d'environnement
            with pytest.raises(Exception):
                import importlib
                import src.app.database
                importlib.reload(src.app.database)
