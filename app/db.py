from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import get_settings


settings = get_settings()

# Production-ready connection pool
engine = create_engine(
    settings.DATABASE_URL,
    future=True,
    pool_pre_ping=True,  # Проверка соединения перед использованием
    pool_size=10,  # Базовый размер пула
    max_overflow=5,  # Дополнительные соединения при пике
    pool_recycle=3600,  # Пересоздавать соединения через 1 час
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """⚠️ ТОЛЬКО для локальной разработки! В production использовать Alembic."""
    Base.metadata.create_all(bind=engine)
