from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.checkpoint import Checkpoint, CheckpointStatusHistory
from app.schemas.checkpoint_schema import (
    CheckpointCreate,
    CheckpointUpdate,
    CheckpointResponse,
    CheckpointDetailsResponse,
    CheckpointStatusHistoryCreate,
    CheckpointStatusHistoryResponse,
)

router = APIRouter()


@router.get("/", response_model=list[CheckpointResponse])
def get_checkpoints(
    db: Session = Depends(get_db),
    city: str | None = None,
    status: str | None = None,
    search: str | None = None,
    sort_by: str = Query("id", pattern="^(id|name|city|created_at|current_status)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    query = db.query(Checkpoint)

    if city:
        query = query.filter(Checkpoint.city == city)

    if status:
        query = query.filter(Checkpoint.current_status == status)

    if search:
        query = query.filter(Checkpoint.name.ilike(f"%{search}%"))

    if sort_by == "name":
        query = query.order_by(Checkpoint.name)
    elif sort_by == "city":
        query = query.order_by(Checkpoint.city)
    elif sort_by == "created_at":
        query = query.order_by(Checkpoint.created_at.desc())
    elif sort_by == "current_status":
        query = query.order_by(Checkpoint.current_status)
    else:
        query = query.order_by(Checkpoint.id)

    return query.offset(skip).limit(limit).all()


@router.get("/{checkpoint_id}", response_model=CheckpointDetailsResponse)
def get_checkpoint_by_id(
    checkpoint_id: int,
    db: Session = Depends(get_db),
):
    checkpoint = db.query(Checkpoint).filter(Checkpoint.id == checkpoint_id).first()

    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")

    return checkpoint


@router.post("/", response_model=CheckpointResponse)
def create_checkpoint(
    checkpoint: CheckpointCreate,
    db: Session = Depends(get_db),
):
    new_checkpoint = Checkpoint(**checkpoint.model_dump())

    db.add(new_checkpoint)
    db.commit()
    db.refresh(new_checkpoint)

    history = CheckpointStatusHistory(
        checkpoint_id=new_checkpoint.id,
        old_status=None,
        new_status=new_checkpoint.current_status,
        reason="Initial checkpoint status",
        changed_by="system",
    )

    db.add(history)
    db.commit()

    return new_checkpoint


@router.put("/{checkpoint_id}", response_model=CheckpointResponse)
def update_checkpoint(
    checkpoint_id: int,
    checkpoint_data: CheckpointUpdate,
    db: Session = Depends(get_db),
):
    checkpoint = db.query(Checkpoint).filter(Checkpoint.id == checkpoint_id).first()

    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")

    update_data = checkpoint_data.model_dump(exclude_unset=True)

    old_status = checkpoint.current_status

    for field, value in update_data.items():
        setattr(checkpoint, field, value)

    if "current_status" in update_data and update_data["current_status"] != old_status:
        history = CheckpointStatusHistory(
            checkpoint_id=checkpoint.id,
            old_status=old_status,
            new_status=update_data["current_status"],
            reason="Status updated",
            changed_by="system",
        )
        db.add(history)

    db.commit()
    db.refresh(checkpoint)

    return checkpoint


@router.patch("/{checkpoint_id}/status", response_model=CheckpointStatusHistoryResponse)
def update_checkpoint_status(
    checkpoint_id: int,
    status_data: CheckpointStatusHistoryCreate,
    db: Session = Depends(get_db),
):
    checkpoint = db.query(Checkpoint).filter(Checkpoint.id == checkpoint_id).first()

    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")

    old_status = checkpoint.current_status
    checkpoint.current_status = status_data.new_status

    history = CheckpointStatusHistory(
        checkpoint_id=checkpoint.id,
        old_status=old_status,
        new_status=status_data.new_status,
        reason=status_data.reason,
        changed_by=status_data.changed_by,
    )

    db.add(history)
    db.commit()
    db.refresh(history)

    return history


@router.delete("/{checkpoint_id}")
def delete_checkpoint(
    checkpoint_id: int,
    db: Session = Depends(get_db),
):
    checkpoint = db.query(Checkpoint).filter(Checkpoint.id == checkpoint_id).first()

    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")

    db.delete(checkpoint)
    db.commit()

    return {"message": "Checkpoint deleted successfully"}