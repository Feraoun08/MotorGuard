from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.config import BackendConfig


def create_postgres_engine(config: BackendConfig):
    return create_engine(
        config.postgres_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )


def create_session_factory(engine):
    return sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )