from app.models.base import Base
from app.models import *
from sqlalchemy import Column, Integer, ForeignKey, ForeignKeyConstraint, Table
from sqlalchemy.types import (
    FLOAT,
    JSON,
    BOOLEAN,
    SMALLINT,
    BIGINT,
    Text,
    TIMESTAMP,
    LargeBinary
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, drop_database, create_database
from sqlalchemy.sql import func

import logging.config

# logging.config.fileConfig('logging.ini') # having this uncommented this seems to break things
logger = logging.getLogger(__name__)

def create_db(connection_str):
    engine = create_engine(connection_str)
    if not database_exists(engine.url):
        create_database(engine.url)


def drop_db(connection_str):
    engine = create_engine(connection_str)
    drop_database(engine.url)


def create_schema(connection_str):
    engine = create_engine(connection_str)
    Base.metadata.create_all(engine)
    logging.info(Base.metadata.tables)
    engine.dispose()


if __name__ == "__main__":
    try:
        from db_config_parser import get_conn_str
    except ModuleNotFoundError:
        raise ModuleNotFoundError(
            'Database credentials missing! '
            'Change default.database.ini and save as database.ini')
    conn_str = get_conn_str()
    create_db(conn_str)
    create_schema(conn_str)
