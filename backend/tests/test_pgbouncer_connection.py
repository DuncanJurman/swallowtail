"""
Test suite for verifying PgBouncer compatibility with SQLAlchemy + asyncpg.
These tests confirm that the database connection works correctly with connection pooling.

Run with:
    USE_POOLED_CONNECTION=true PYTHONPATH=. poetry run pytest tests/test_pgbouncer_connection.py -v
    
Or directly:
    USE_POOLED_CONNECTION=true PYTHONPATH=. poetry run python tests/test_pgbouncer_connection.py
"""

import asyncio
import os
import pytest
from typing import Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class TestPgBouncerConnection:
    """Test suite for PgBouncer pooled connection compatibility."""
    
    @pytest.mark.asyncio
    async def test_pooled_connection_basic(self):
        """Test that basic queries work with pooled connection."""
        # Import after environment is set
        from src.core.database import engine
        
        # Use engine directly to avoid transaction issues in tests
        async with engine.connect() as conn:
            # Test basic query
            result = await conn.execute(text("SELECT 1"))
            assert result.scalar() == 1
            
            # Test database info query
            result = await conn.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            assert db_name is not None
            assert db_name == "postgres"
    
    @pytest.mark.asyncio
    async def test_no_prepared_statement_errors(self):
        """Test that multiple queries don't cause DuplicatePreparedStatementError."""
        from src.core.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as session:
            # Execute the same query multiple times
            # This would fail with DuplicatePreparedStatementError without our fix
            for i in range(10):
                result = await session.execute(text(f"SELECT {i} as num"))
                assert result.scalar() == i
            
            # Execute different queries in sequence
            queries = [
                "SELECT version()",
                "SELECT current_timestamp",
                "SELECT current_user",
                "SELECT pg_backend_pid()",
            ]
            
            for query in queries:
                result = await session.execute(text(query))
                assert result.scalar() is not None
    
    @pytest.mark.asyncio
    async def test_transaction_handling(self):
        """Test that transactions work correctly with pooled connection."""
        from src.core.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as session:
            # Start a transaction
            async with session.begin():
                # Multiple queries within transaction
                result = await session.execute(text("SELECT 1"))
                assert result.scalar() == 1
                
                result = await session.execute(text("SELECT 2"))
                assert result.scalar() == 2
            
            # Transaction should be committed
            # Verify connection is still usable
            result = await session.execute(text("SELECT 3"))
            assert result.scalar() == 3
    
    @pytest.mark.asyncio
    async def test_connection_pool_status(self):
        """Test that we can check connection pool status."""
        from src.core.database import AsyncSessionLocal
        from src.api.routes.health import check_database_pool
        
        async with AsyncSessionLocal() as session:
            status = await check_database_pool(session)
            
            assert status.connected == True
            assert status.connection_type == "transaction_pooler"
            assert status.database_url_type == "DATABASE_URL"
            assert status.database_name == "postgres"
            assert status.postgresql_version is not None
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        """Test that the health endpoint returns database status."""
        # Note: TestClient has issues with async connections in this context
        # so we test the underlying function directly
        from src.api.routes.health import check_database_pool
        from src.core.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as session:
            # Test the database pool check function used by health endpoint
            status = await check_database_pool(session)
            
            # Verify the response structure matches what health endpoint returns
            assert status.connected == True
            assert status.connection_type == "transaction_pooler"
            assert status.database_url_type == "DATABASE_URL"
            assert status.database_name is not None
            assert status.postgresql_version is not None
            assert status.error is None
    
    @pytest.mark.asyncio
    async def test_connection_configuration(self):
        """Test that connection is configured correctly for PgBouncer."""
        from src.core.database import engine, DATABASE_URL
        
        # Verify configuration
        assert "asyncpg" in DATABASE_URL
        assert "pooler.supabase.com:6543" in DATABASE_URL
        
        # Check connect_args (these are set at engine creation)
        # The key settings are:
        # - statement_cache_size = 0
        # - prepared_statement_name_func generates unique names
        
        # Test that engine is functional
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            assert result.scalar() == 1


async def run_all_tests():
    """Run all tests as a standalone script."""
    print("\n" + "=" * 60)
    print("PGBOUNCER CONNECTION TEST SUITE")
    print("=" * 60 + "\n")
    
    test_suite = TestPgBouncerConnection()
    
    tests = [
        ("Basic Connection", test_suite.test_pooled_connection_basic),
        ("No Prepared Statement Errors", test_suite.test_no_prepared_statement_errors),
        ("Transaction Handling", test_suite.test_transaction_handling),
        ("Connection Pool Status", test_suite.test_connection_pool_status),
        ("Health Endpoint", test_suite.test_health_endpoint),
        ("Connection Configuration", test_suite.test_connection_configuration),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"Running: {test_name}...")
        try:
            await test_func()
            print(f"  ✅ PASSED\n")
            passed += 1
        except Exception as e:
            print(f"  ❌ FAILED: {e}\n")
            failed += 1
    
    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! PgBouncer connection is working correctly!")
        print("The fix using statement_cache_size=0 and unique statement names works!")
    else:
        print(f"⚠️  Some tests failed. Please check the configuration.")
    
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    # Run as standalone script
    success = asyncio.run(run_all_tests())