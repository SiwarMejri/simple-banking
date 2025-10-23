import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from src.app.create_tables import create_tables, get_inspector, main

class TestCreateTablesDetailed:
    """Tests détaillés pour create_tables.py"""
    
    @patch('src.app.create_tables.Base.metadata.create_all')
    @patch('src.app.create_tables.engine')
    def test_create_tables_success(self, mock_engine, mock_create_all):
        """Test que create_tables() fonctionne correctement"""
        # Appeler la fonction
        create_tables()
        
        # Vérifier les appels
        mock_create_all.assert_called_once_with(bind=mock_engine)
    
    @patch('src.app.create_tables.create_tables')
    @patch('src.app.create_tables.print')
    def test_main_success(self, mock_print, mock_create_tables):
        """Test que main() appelle create_tables"""
        # Appeler main
        main()
        
        # Vérifier les appels
        mock_create_tables.assert_called_once()
        mock_print.assert_called_once_with("✅ Tables créées avec succès!")
    
    @patch('src.app.create_tables.inspect')
    def test_get_inspector(self, mock_inspect):
        """Test la fonction get_inspector"""
        mock_engine = MagicMock()
        result = get_inspector(mock_engine)
        
        # Vérifier que inspect a été appelé
        mock_inspect.assert_called_once_with(mock_engine)
