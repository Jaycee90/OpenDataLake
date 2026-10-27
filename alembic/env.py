import sys
from pathlib import Path
from logging.config import fileConfig
import os
from sqlalchemy import engine_from_config, pool
from alembic import context
# Make src/opendatalake importable
sys.path.append(
    str(Path(__file__).resolve().parents[1] / "src")
)

from opendatalake.config.settings import Settings
from opendatalake.database.models.base import Base
from opendatalake.database.models.event import Event
from opendatalake.database.models.dim_date import DimDate
from opendatalake.database.models.dim_venue import DimVenue
from opendatalake.database.models.dim_category import DimCategory
from opendatalake.database.models.fact_events import FactEvent

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
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# settings = Settings.load()  # Load settings from environment variables

# config.set_main_option(
#     "sqlalchemy.url",
#     settings.database_url,
# )
settings = Settings.load()

database_url = os.environ.get(
    "ALEMBIC_DATABASE_URL",
    settings.database_url,
)

config.set_main_option(
    "sqlalchemy.url",
    database_url,
)

'''
Since analytics schema contains views and materialized views that aren't represented as SQLAlchemy tables,
we should prevent Alembic from accidentally treating those objects as tables to remove. This temporarily prevents
autogenerate from proposing deletion of existing database tables that aren't registered in SQLAlchemy.
It doesn't prevent explicit migration operations, and we'll refine the filtering later.
'''
def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and reflected and compare_to is None:
        return False

    return True

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
        include_schemas=True,
        include_object=include_object,
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
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
