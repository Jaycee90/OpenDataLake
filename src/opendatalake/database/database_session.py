import logging

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from opendatalake.config.settings import Settings
from opendatalake.database.models.base import Base
# Import models so SQLAlchemy registers them.
from opendatalake.database.models.event import Event

logger = logging.getLogger(__name__)

'''
What is pool_pre_ping=True?
Before SQLAlchemy reuses a pooled connection, it verifies that the connection is still alive. 
That helps recover from stale or disconnected connections without making repositories handle that concern.
'''
def create_database_engine(settings: Settings) -> Engine:
    logger.info("Creating PostgreSQL database engine")

    return create_engine(
        settings.database_url,
        pool_pre_ping=True,
    )

def create_session_factory(engine: Engine,) -> sessionmaker[Session]:
    return sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )

def create_database_tables(engine: Engine) -> None:
    Base.metadata.create_all(bind=engine)