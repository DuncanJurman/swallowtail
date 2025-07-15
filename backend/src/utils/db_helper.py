"""Database connection helper for direct asyncpg connections."""

import re
import asyncpg
from typing import Optional
from urllib.parse import unquote

from src.core.config import get_settings


async def get_asyncpg_connection(use_direct_url: bool = True) -> asyncpg.Connection:
    """Get a direct asyncpg connection, parsing the database URL properly."""
    settings = get_settings()
    
    # Choose which URL to use
    db_url = settings.database_direct_url if use_direct_url else settings.database_url
    
    if not db_url:
        raise ValueError("Database URL not configured")
    
    # Parse the PostgreSQL URL
    # Handle both postgresql:// and postgres:// prefixes
    pattern = r'(?:postgresql|postgres)://([^:]+):([^@]+)@([^:/]+)(?::(\d+))?/([^?]+)(?:\?(.+))?'
    match = re.match(pattern, db_url)
    
    if not match:
        raise ValueError(f"Invalid database URL format")
    
    user, password, host, port, database, params = match.groups()
    
    # URL decode the password
    password = unquote(password)
    
    # Default port if not specified
    port = int(port) if port else 5432
    
    # Parse SSL mode from params if present
    ssl_mode = None
    if params:
        for param in params.split('&'):
            if param.startswith('sslmode='):
                ssl_mode = param.split('=')[1]
                break
    
    # Connect with proper parameters
    connection_params = {
        'host': host,
        'port': port,
        'user': user,
        'password': password,
        'database': database,
        # Disable statement caching for pgbouncer compatibility
        'statement_cache_size': 0,
    }
    
    # Add SSL if specified
    if ssl_mode == 'require':
        connection_params['ssl'] = 'require'
    
    return await asyncpg.connect(**connection_params)