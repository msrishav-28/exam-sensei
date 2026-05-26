"""
Database engine + session factory.

Reads DATABASE_URL via settings so the same code path works for
local SQLite development and Supabase (Postgres) in production.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from config import settings


def _engine_kwargs(url: str) -> dict:
    """Pick connection arguments that match the backend driver."""
    if url.startswith("sqlite"):
        # SQLite needs check_same_thread off so FastAPI's threadpool can share
        # the connection across requests in dev.
        return {"connect_args": {"check_same_thread": False}}

    # Postgres / Supabase: enable pool_pre_ping so we recover transparently
    # when Supabase drops idle connections. Modest pool sizes — we expect
    # tens of concurrent users at most.
    return {
        "pool_pre_ping": True,
        "pool_size": 5,
        "max_overflow": 10,
        "pool_recycle": 1800,
    }


engine = create_engine(settings.database_url, **_engine_kwargs(settings.database_url))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)
