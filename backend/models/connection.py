import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base, GUID, JSONType


class Connection(Base):
    """A connection to an external system (API or DB)."""

    __tablename__ = "connections"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(10), nullable=False)  # "api" or "db"

    # API fields
    base_url: Mapped[str | None] = mapped_column(String(1024))
    auth_type: Mapped[str | None] = mapped_column(String(50))  # "bearer", "basic", "api_key", "none"
    auth_config: Mapped[dict | None] = mapped_column(JSONType())  # token, username/password, etc.
    headers: Mapped[dict | None] = mapped_column(JSONType())

    # DB fields
    db_type: Mapped[str | None] = mapped_column(String(50))  # "postgresql", "mysql", "mssql"
    db_host: Mapped[str | None] = mapped_column(String(255))
    db_port: Mapped[int | None] = mapped_column()
    db_name: Mapped[str | None] = mapped_column(String(255))
    db_user: Mapped[str | None] = mapped_column(String(255))
    db_password: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
