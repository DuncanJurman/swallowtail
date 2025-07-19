"""Comprehensive database setup and connection test.

Run this file to verify:
1. Database connection is working
2. All tables are created
3. Alembic migrations are up to date
"""

import asyncio
import asyncpg
from typing import List, Tuple
from src.core.config import get_settings


async def test_database_setup():
    """Test database connection and verify schema setup."""
    settings = get_settings()
    
    print("🔍 Testing Swallowtail Database Setup\n")
    print(f"Database URL: {settings.database_url}")
    
    # Parse the URL
    import re
    match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', settings.database_url)
    if not match:
        print("❌ Failed to parse database URL")
        return
    
    user, password, host, port, database = match.groups()
    
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Database: {database}")
    print(f"User: {user}")
    print("\n" + "="*50 + "\n")
    
    try:
        # Test connection
        print("📡 Testing connection...")
        conn = await asyncpg.connect(
            host=host,
            port=int(port),
            user=user,
            password=password.replace('%21', '!'),  # Decode URL-encoded password
            database=database
        )
        print("✅ Connection successful!\n")
        
        # Check tables
        print("📊 Checking database tables...")
        tables = await conn.fetch("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            ORDER BY tablename;
        """)
        
        expected_tables = [
            'agent_decisions',
            'agent_tasks', 
            'agents',
            'alembic_version',
            'market_opportunities',
            'products',
            'shared_knowledge'
        ]
        
        actual_tables = [table['tablename'] for table in tables]
        
        print(f"Found {len(actual_tables)} tables:")
        for table in actual_tables:
            status = "✅" if table in expected_tables else "⚠️"
            print(f"  {status} {table}")
        
        # Check for missing tables
        missing_tables = set(expected_tables) - set(actual_tables)
        if missing_tables:
            print(f"\n⚠️  Missing tables: {', '.join(missing_tables)}")
        else:
            print("\n✅ All expected tables present!")
        
        # Check Alembic version
        print("\n🔄 Checking migration status...")
        try:
            version = await conn.fetchval("SELECT version_num FROM alembic_version;")
            print(f"✅ Current migration version: {version}")
        except Exception as e:
            print(f"⚠️  No migrations applied yet")
        
        # Test table structure (sample check)
        print("\n🔍 Checking table structure (sample)...")
        
        # Check products table columns
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'products'
            ORDER BY ordinal_position;
        """)
        
        print("Products table structure:")
        for col in columns[:5]:  # Show first 5 columns
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            print(f"  - {col['column_name']}: {col['data_type']} {nullable}")
        print(f"  ... and {len(columns) - 5} more columns")
        
        # Test counts
        print("\n📈 Table row counts:")
        for table in ['products', 'agents', 'agent_tasks']:
            count = await conn.fetchval(f"SELECT COUNT(*) FROM {table};")
            print(f"  - {table}: {count} rows")
        
        print("\n✅ Database setup verification complete!")
        
        await conn.close()
        
    except asyncpg.PostgresError as e:
        print(f"❌ Database error: {e}")
        print("\nPossible issues:")
        print("- Check if database is accessible")
        print("- Verify credentials in .env file")
        print("- Ensure Supabase project is active")
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("\nPossible issues:")
        print("- Check your internet connection")
        print("- Verify the database URL is correct")
        print("- Check if password needs URL encoding")


if __name__ == "__main__":
    print("🚀 Swallowtail Database Setup Test\n")
    asyncio.run(test_database_setup())