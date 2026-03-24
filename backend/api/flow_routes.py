import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.engine.executor import FlowExecutor
from backend.models.flow import Flow, FlowRun
from backend.rql.parser import parse_rql
from backend.schemas.flow import (
    FlowCreate, FlowOut, FlowUpdate,
    FlowRunOut, RQLValidateRequest, RQLValidateResponse,
)

router = APIRouter(prefix="/api/flows", tags=["flows"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[FlowOut])
def list_flows(db: Session = Depends(get_db)):
    return db.query(Flow).order_by(Flow.created_at.desc()).all()


@router.get("/{flow_id}", response_model=FlowOut)
def get_flow(flow_id: uuid.UUID, db: Session = Depends(get_db)):
    flow = db.get(Flow, flow_id)
    if not flow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return flow


@router.post("", response_model=FlowOut, status_code=status.HTTP_201_CREATED)
def create_flow(body: FlowCreate, db: Session = Depends(get_db)):
    # Validate RQL first
    program = parse_rql(body.rql)

    flow = Flow(
        name=body.name,
        rql=body.rql,
        source_connection_id=body.source_connection_id,
        target_connection_id=body.target_connection_id,
        source_path=body.source_path,
        target_path=body.target_path,
        trigger_type=program.trigger.type,
        trigger_interval_minutes=program.trigger.interval_minutes,
    )
    db.add(flow)
    db.commit()
    db.refresh(flow)
    return flow


@router.put("/{flow_id}", response_model=FlowOut)
def update_flow(flow_id: uuid.UUID, body: FlowUpdate, db: Session = Depends(get_db)):
    flow = db.get(Flow, flow_id)
    if not flow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    update_data = body.model_dump(exclude_unset=True)

    if "rql" in update_data:
        program = parse_rql(update_data["rql"])
        update_data["trigger_type"] = program.trigger.type
        update_data["trigger_interval_minutes"] = program.trigger.interval_minutes

    for key, value in update_data.items():
        setattr(flow, key, value)
    db.commit()
    db.refresh(flow)
    return flow


@router.delete("/{flow_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_flow(flow_id: uuid.UUID, db: Session = Depends(get_db)):
    flow = db.get(Flow, flow_id)
    if not flow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    db.delete(flow)
    db.commit()


@router.post("/{flow_id}/run", response_model=FlowRunOut)
async def run_flow(flow_id: uuid.UUID, db: Session = Depends(get_db)):
    """Manually trigger a flow execution."""
    flow = db.get(Flow, flow_id)
    if not flow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    program = parse_rql(flow.rql)
    executor = FlowExecutor(db, flow, program)
    run = await executor.run()
    return run


@router.get("/{flow_id}/runs", response_model=list[FlowRunOut])
def list_runs(flow_id: uuid.UUID, db: Session = Depends(get_db)):
    return (
        db.query(FlowRun)
        .filter(FlowRun.flow_id == flow_id)
        .order_by(FlowRun.started_at.desc())
        .limit(50)
        .all()
    )


@router.post("/validate", response_model=RQLValidateResponse)
def validate_rql(body: RQLValidateRequest):
    """Validate RQL syntax without executing."""
    try:
        program = parse_rql(body.rql)
        return RQLValidateResponse(
            valid=True,
            source=program.source,
            target=program.target,
            mapping_count=len(program.mappings),
            rule_count=len(program.rules),
            trigger_type=program.trigger.type,
        )
    except (SyntaxError, ValueError) as e:
        return RQLValidateResponse(valid=False, error=str(e))
