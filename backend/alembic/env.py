from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Import our models and settings
from src.core.database import Base
from src.core.config import get_settings

# Import all models to ensure they are registered with Base.metadata
import src.models.database  # Core database models
import src.models.user  # User model
import src.models.instance  # Instance model
import src.models.tiktok_credentials  # TikTok credentials model
import src.models.checkpoint  # Checkpoint model
import src.models.product  # Product model
import src.models.research  # Research model

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Get database URL from settings
settings = get_settings()

# IMPORTANT: Use session pooler for migrations on Railway (IPv4 support)
# Session pooler (port 5432) supports DDL operations needed for migrations
# Direct connection fails on Railway due to IPv6
if settings.database_session_pooler_url:
    # Always prefer session pooler when available (IPv4 compatible)
    database_url = settings.database_session_pooler_url
    print("Using session pooler connection for migrations (IPv4 compatible)")
elif settings.database_url:
    # Fall back to transaction pooler if session pooler not available
    # This may have issues with some DDL operations
    database_url = settings.database_url
    print("WARNING: Using transaction pooler for migrations. Some DDL operations may fail.")
else:
    # This should never happen in production
    raise ValueError("No database URL configured for migrations")

# Escape % for ConfigParser
database_url = database_url.replace("%", "%%")
config.set_main_option("sqlalchemy.url", database_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()