from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from constants import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(engine, autoflush=False, expire_on_commit=False)


def get_session():
    """Returns a new sqlalchemy session."""

    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
