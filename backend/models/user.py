import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base, GUID


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
