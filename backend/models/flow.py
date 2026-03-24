import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, Boolean, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base, GUID


class Flow(Base):
    """An integration flow defined by RQL."""

    __tablename__ = "flows"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    rql: Mapped[str] = mapped_column(Text, nullable=False)

    source_connection_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("connections.id"))
    target_connection_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("connections.id"))

    source_path: Mapped[str] = mapped_column(String(512))  # API endpoint or DB table
    target_path: Mapped[str] = mapped_column(String(512))

    trigger_type: Mapped[str] = mapped_column(String(20), default="manual")  # "manual", "interval"
    trigger_interval_minutes: Mapped[int | None] = mapped_column()

    active: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class FlowRun(Base):
    """A single execution record of a flow."""

    __tablename__ = "flow_runs"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    flow_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("flows.id"))

    status: Mapped[str] = mapped_column(String(20), default="running")  # "running", "success", "error"
    records_processed: Mapped[int] = mapped_column(default=0)
    records_failed: Mapped[int] = mapped_column(default=0)
    error_message: Mapped[str | None] = mapped_column(Text)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
