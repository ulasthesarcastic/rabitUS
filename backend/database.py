import json
import uuid

from sqlalchemy import String, Text, TypeDecorator, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from backend.config import settings

connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


# ── Portable column types (work on SQLite + PostgreSQL) ──

class GUID(TypeDecorator):
    """UUID stored as CHAR(36) on SQLite, native UUID on PostgreSQL."""
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return uuid.UUID(value)
        return value


class JSONType(TypeDecorator):
    """JSON stored as TEXT on SQLite, native JSONB on PostgreSQL."""
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return value


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
