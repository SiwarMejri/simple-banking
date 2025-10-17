import pytest
from unittest.mock import patch, MagicMock

# Test pour s'assurer que Base.metadata.create_all est appelé
def test_create_tables_called():
    with patch("src.app.create_tables.Base.metadata.create_all") as mock_create_all, \
         patch("builtins.print") as mock_print:
        import src.app.create_tables  # L'import exécute le code de création
        mock_create_all.assert_called_once()
        mock_print.assert_called_with("✅ Tables créées avec succès dans la base 'banking'.")
