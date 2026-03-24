import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.models.connection import Connection
from backend.schemas.connection import ConnectionCreate, ConnectionOut, ConnectionUpdate

router = APIRouter(prefix="/api/connections", tags=["connections"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[ConnectionOut])
def list_connections(db: Session = Depends(get_db)):
    return db.query(Connection).order_by(Connection.created_at.desc()).all()


@router.get("/{connection_id}", response_model=ConnectionOut)
def get_connection(connection_id: uuid.UUID, db: Session = Depends(get_db)):
    conn = db.get(Connection, connection_id)
    if not conn:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return conn


@router.post("", response_model=ConnectionOut, status_code=status.HTTP_201_CREATED)
def create_connection(body: ConnectionCreate, db: Session = Depends(get_db)):
    conn = Connection(**body.model_dump())
    db.add(conn)
    db.commit()
    db.refresh(conn)
    return conn


@router.put("/{connection_id}", response_model=ConnectionOut)
def update_connection(connection_id: uuid.UUID, body: ConnectionUpdate, db: Session = Depends(get_db)):
    conn = db.get(Connection, connection_id)
    if not conn:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    for key, value in body.model_dump().items():
        setattr(conn, key, value)
    db.commit()
    db.refresh(conn)
    return conn


@router.delete("/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_connection(connection_id: uuid.UUID, db: Session = Depends(get_db)):
    conn = db.get(Connection, connection_id)
    if not conn:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    db.delete(conn)
    db.commit()
