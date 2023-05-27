import os

import pytest
import sqlalchemy.engine.url
from pytest_postgresql.janitor import DatabaseJanitor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db import Base

DATABASE_URL = os.getenv("TEST_DATABASE_URL")

test_engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(
    bind=test_engine, autoflush=False, expire_on_commit=False
)


@pytest.fixture(scope="session")
def database():
    """
    Create a Postgres database for the tests, and drop it when the tests are done.
    """
    DB_OPTS = sqlalchemy.engine.url.make_url(DATABASE_URL).translate_connect_args()
    pg_host = DB_OPTS.get("host")
    pg_port = DB_OPTS.get("port")
    pg_user = DB_OPTS.get("username")
    pg_pass = DB_OPTS.get("password")
    pg_db = DB_OPTS["database"]

    janitor = DatabaseJanitor(pg_user, pg_host, pg_port, pg_db, 15.3, pg_pass)
    janitor.init()
    yield
    janitor.drop()


@pytest.fixture(scope="session")
def tables():
    """
    Create all tables in the schema. This is executed only once per session.
    """
    Base.metadata.create_all(test_engine)
    yield
    Base.metadata.drop_all(test_engine)


@pytest.fixture(scope="function")
def session(database, tables):
    """
    Creates a new database session for a test.
    """
    connection = test_engine.connect()
    transaction = connection.begin()

    session = TestingSessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()
