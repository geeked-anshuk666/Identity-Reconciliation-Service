from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
import os

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.models.contact import Base
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
    from app.config import settings
    
    # Override the sqlalchemy.url with our settings
    # Check if DATABASE_URL is provided by Render
    render_database_url = os.environ.get("DATABASE_URL")
    if render_database_url:
        sync_database_url = render_database_url
    else:
        # Convert async URL to sync URL for Alembic
        sync_database_url = settings.database_url
    
    # Convert to sync URL format for Alembic
    if sync_database_url.startswith('postgresql+psycopg2://'):
        sync_database_url = sync_database_url.replace('postgresql+psycopg2://', 'postgresql://')
    elif sync_database_url.startswith('postgresql+asyncpg://'):
        sync_database_url = sync_database_url.replace('postgresql+asyncpg://', 'postgresql://')
    elif sync_database_url.startswith('sqlite+aiosqlite://'):
        sync_database_url = sync_database_url.replace('sqlite+aiosqlite://', 'sqlite://')
    
    config.set_main_option('sqlalchemy.url', sync_database_url)
    
    # Use synchronous engine for Alembic
    from sqlalchemy import create_engine
    
    connectable = create_engine(
        sync_database_url,
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