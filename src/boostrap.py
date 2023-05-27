from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from constants import DATABASE_URL


def get_session():
    engine = create_engine(DATABASE_URL)
    return sessionmaker(engine, autoflush=False, expire_on_commit=False)()
