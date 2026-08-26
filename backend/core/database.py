import logging
from typing import Generator, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from supabase import create_client, Client

from backend.core.config import settings

logger = logging.getLogger(__name__)

# Base Model for SQLAlchemy
Base = declarative_base()

# SQLAlchemy Setup (Sync and Engine helpers)
db_url = settings.SYNC_DATABASE_URL
if db_url.startswith("postgresql+asyncpg://"):
    db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")

engine = create_engine(
    db_url,
    connect_args={"check_same_thread": False} if "sqlite" in db_url else {},
    echo=False,
    pool_pre_ping=True if "sqlite" not in db_url else False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency that yields a database session and safely closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_supabase_client() -> Optional[Client]:
    """
    Returns an initialized Supabase Client if valid credentials are provided,
    otherwise returns None for graceful offline / local development.
    """
    if (
        settings.SUPABASE_URL
        and "mock" not in settings.SUPABASE_URL
        and settings.SUPABASE_KEY
        and "mock" not in settings.SUPABASE_KEY
    ):
        try:
            return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        except Exception as e:
            logger.warning(f"Failed to initialize live Supabase client: {e}")
            return None
    return None


def get_supabase_admin_client() -> Optional[Client]:
    """Returns the Supabase service role client for privileged backend tasks."""
    if (
        settings.SUPABASE_URL
        and "mock" not in settings.SUPABASE_URL
        and settings.SUPABASE_SERVICE_ROLE_KEY
        and "mock" not in settings.SUPABASE_SERVICE_ROLE_KEY
    ):
        try:
            return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        except Exception as e:
            logger.warning(f"Failed to initialize live Supabase admin client: {e}")
            return None
    return None


def init_db():
    """Initializes tables in database."""
    Base.metadata.create_all(bind=engine)
