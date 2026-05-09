"""Database connection utilities for FastAPI.

Provides a SQLAlchemy engine and a scoped session factory (SessionLocal) that can be
imported by the application. The configuration reads the database URL from the
environment variable ``DATABASE_URL`` and falls back to a local SQLite file for
development.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Default to a SQLite file in the project root for simplicity.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fastapi_app.db")

# ``check_same_thread=False`` is required for SQLite when used with FastAPI's
# async context.
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# SessionLocal will be used by dependency injection to provide a DB session per request.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models – the existing models already inherit from
# ``DeclarativeBase`` in ``models.py``; we expose it here for any new models.
Base = declarative_base()
