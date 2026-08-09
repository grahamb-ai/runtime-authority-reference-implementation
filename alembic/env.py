## @file env.py
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Alembic migration environment: wires the migration runner to the app's database configuration.
#
"""Alembic migration environment."""

import os
import sys
from logging.config import fileConfig


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

from app.config import DATABASE_URL

# Import models so they register on SQLModel.metadata.
from app.models import order, rule  

config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata

## @fn run_migrations_offline()
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Run migrations in 'offline' mode, emitting SQL without a live database connection.
#  @return None.
#
def run_migrations_offline() -> None:
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

## @fn run_migrations_online()
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Run migrations in 'online' mode, against a live database connection.
#  @return None.
#
def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
