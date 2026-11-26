"""SQLAlchemy engine, session factory, and initialization for SQLite & PostgreSQL/Supabase."""

from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import get_settings

settings = get_settings()
db_url = settings.normalized_database_url

connect_args = {}
if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    db_url,
    connect_args=connect_args,
    pool_pre_ping=True,
    future=True,
)

if db_url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
Base = declarative_base()


def get_db():
    """FastAPI dependency yielding a scoped database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables if they do not exist and apply safe additive migrations."""
    import app.models.entities  # noqa: F401

    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    if inspector.has_table("user_profiles"):
        cols = {col["name"] for col in inspector.get_columns("user_profiles")}
        if "preferred_language" not in cols:
            with engine.begin() as conn:
                conn.execute(
                    text(
                        "ALTER TABLE user_profiles ADD COLUMN preferred_language VARCHAR(8) NOT NULL DEFAULT 'en'"
                    )
                )
