import uuid
from datetime import datetime

from pydantic import BaseModel


class ConnectionCreate(BaseModel):
    name: str
    type: str  # "api" or "db"

    # API
    base_url: str | None = None
    auth_type: str | None = None
    auth_config: dict | None = None
    headers: dict | None = None

    # DB
    db_type: str | None = None
    db_host: str | None = None
    db_port: int | None = None
    db_name: str | None = None
    db_user: str | None = None
    db_password: str | None = None


class ConnectionUpdate(ConnectionCreate):
    pass


class ConnectionOut(ConnectionCreate):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
