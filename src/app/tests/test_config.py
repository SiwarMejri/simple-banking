# tests/test_config.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base

# Configuration de la base de données de test
TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="session")
def test_engine():
    """Moteur de base de données de test pour la session."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    
    # Créer toutes les tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Nettoyer après tous les tests
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(test_engine):
    """Session de base de données pour chaque test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(autocommit=False, autoflush=False, bind=connection)()
    
    yield session
    
    # Rollback et fermeture
    session.close()
    transaction.rollback()
    connection.close()
