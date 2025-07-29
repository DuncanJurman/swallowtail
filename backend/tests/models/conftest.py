"""Test configuration for model tests."""

import pytest
import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool, NullPool
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from src.core.database import Base
from src.core.config import get_settings


@pytest.fixture(scope="session")
def test_database_url():
    """Get test database URL."""
    settings = get_settings()
    base_url = settings.database_url
    
    # Replace database name with test database
    if "postgres" in base_url:
        parts = base_url.rsplit("/", 1)
        test_url = f"{parts[0]}/test_{parts[1]}"
        return test_url
    return base_url


@pytest.fixture(scope="session")
def setup_test_database(test_database_url):
    """Create test database if it doesn't exist."""
    from urllib.parse import urlparse, unquote
    
    settings = get_settings()
    base_url = settings.database_url
    
    # Parse the database URL properly
    parsed = urlparse(base_url)
    host = parsed.hostname
    port = parsed.port or 5432
    user = unquote(parsed.username) if parsed.username else None
    password = unquote(parsed.password) if parsed.password else None
    original_db = parsed.path.lstrip('/')
    test_db = f"test_{original_db}"
    
    # Connect to default postgres database
    conn = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        dbname=original_db
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    try:
        # Drop and recreate test database
        cursor.execute(f"DROP DATABASE IF EXISTS {test_db}")
        cursor.execute(f"CREATE DATABASE {test_db}")
    except Exception as e:
        print(f"Error creating test database: {e}")
    finally:
        cursor.close()
        conn.close()
    
    yield test_database_url
    
    # Cleanup: Drop test database after all tests
    conn = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        dbname=original_db
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"DROP DATABASE IF EXISTS {test_db}")
    except Exception as e:
        print(f"Error dropping test database: {e}")
    finally:
        cursor.close()
        conn.close()


@pytest.fixture(scope="function")
def db_session(setup_test_database, test_database_url):
    """Create a test database session."""
    # Create engine with test database
    engine = create_engine(
        test_database_url,
        poolclass=NullPool,  # Disable connection pooling for tests
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Clean up all data after each test
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
        session.close()