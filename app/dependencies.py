"""FastAPI dependencies for database session handling.

Provides a ``get_db`` dependency that yields a SQLAlchemy ``Session`` object
and ensures it is closed after the request.
"""

from typing import Generator

from sqlalchemy.orm import Session

from app.db import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Yield a new database session for a request.

    FastAPI will automatically close the session when the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
