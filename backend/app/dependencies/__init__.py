"""FastAPI dependencies."""

from typing import Generator

from sqlalchemy.orm import Session

from app.db import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Yield a new database session for a request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()