#src/app/tests/test_database.py

import pytest
import os
import sys
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError

# Solution : Importer après le rechargement
def test_database_url_from_env():
    """Test que DATABASE_URL est chargée depuis les variables d'environnement"""
    with patch.dict(os.environ, {'DATABASE_URL': 'sqlite:///test.db'}):
        # Recharger le module correctement
        if 'src.app.database' in sys.modules:
            del sys.modules['src.app.database']
        from src.app import database
        import importlib
        importlib.reload(database)
        
        assert database.DATABASE_URL == 'sqlite:///test.db'

def test_get_db_finally_closes():
    """Test que la session est fermée dans le bloc finally"""
    mock_session = MagicMock()
    
    with patch('src.app.database.SessionLocal', return_value=mock_session):
        db_gen = get_db()
        
        # Simuler l'utilisation normale du générateur
        try:
            db = next(db_gen)
            # Simuler une utilisation
            assert db == mock_session
        except StopIteration:
            pass
        finally:
            # Forcer la fin du générateur
            try:
                next(db_gen)
            except StopIteration:
                pass
        
        # Vérifier que close a été appelé
        mock_session.close.assert_called_once()

def test_database_url_default():
    """Test le comportement quand DATABASE_URL n'est pas définie"""
    with patch.dict(os.environ, clear=True):
        # Recharger le module pour simuler l'absence de variable d'environnement
        if 'src.app.database' in sys.modules:
            del sys.modules['src.app.database']
        if 'os' in sys.modules:
            del sys.modules['os']
        
        with pytest.raises((TypeError, ValueError)):
            from src.app import database
            import importlib
            importlib.reload(database)
