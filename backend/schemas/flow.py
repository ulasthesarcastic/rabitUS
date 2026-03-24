import uuid
from datetime import datetime

from pydantic import BaseModel


class FlowCreate(BaseModel):
    name: str
    rql: str
    source_connection_id: uuid.UUID
    target_connection_id: uuid.UUID
    source_path: str
    target_path: str


class FlowUpdate(BaseModel):
    name: str | None = None
    rql: str | None = None
    source_connection_id: uuid.UUID | None = None
    target_connection_id: uuid.UUID | None = None
    source_path: str | None = None
    target_path: str | None = None
    active: bool | None = None


class FlowOut(BaseModel):
    id: uuid.UUID
    name: str
    rql: str
    source_connection_id: uuid.UUID
    target_connection_id: uuid.UUID
    source_path: str
    target_path: str
    trigger_type: str
    trigger_interval_minutes: int | None
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FlowRunOut(BaseModel):
    id: uuid.UUID
    flow_id: uuid.UUID
    status: str
    records_processed: int
    records_failed: int
    error_message: str | None
    started_at: datetime
    finished_at: datetime | None

    model_config = {"from_attributes": True}


class RQLValidateRequest(BaseModel):
    rql: str


class RQLValidateResponse(BaseModel):
    valid: bool
    error: str | None = None
    source: str | None = None
    target: str | None = None
    mapping_count: int = 0
    rule_count: int = 0
    trigger_type: str | None = None
