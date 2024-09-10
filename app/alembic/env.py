
import logging

import os
import sys
from logging.config import fileConfig

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from alembic import context
from sqlalchemy import engine_from_config, pool
from app.db.base import Base  # Import your models here
from app.db.models import *

from app.core.config import settings  # Import your DB URL from the application


config = context.config

# Manually configure logging to avoid 'formatters' error
if config.config_file_name is not None:
    try:
        fileConfig(config.config_file_name)
    except KeyError as e:
        logging.basicConfig(level=logging.INFO)
        logging.getLogger('alembic').info(f"Manual logging setup due to missing configuration key: {e}")

# Set your database URL dynamically
config.set_main_option('sqlalchemy.url', settings.database_url)

# Add your models' metadata here
target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"}
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section), prefix="sqlalchemy.", poolclass=pool.NullPool
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
