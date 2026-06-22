from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.alert import AlertSubscription, AlertRecord
from app.models.incident import Incident
from app.schemas.alert_schema import (
    AlertSubscriptionCreate,
    AlertSubscriptionResponse,
    AlertRecordResponse,
)
from app.services.alert_service import create_alerts_for_verified_incident

router = APIRouter()


@router.post("/subscriptions", response_model=AlertSubscriptionResponse)
def create_subscription(
    subscription_data: AlertSubscriptionCreate,
    db: Session = Depends(get_db),
):
    subscription = AlertSubscription(**subscription_data.model_dump())

    db.add(subscription)
    db.commit()
    db.refresh(subscription)

    return subscription


@router.get("/subscriptions", response_model=list[AlertSubscriptionResponse])
def get_subscriptions(
    db: Session = Depends(get_db),
    user_identifier: str | None = None,
    area_name: str | None = None,
    category: str | None = None,
    active_only: bool = True,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    query = db.query(AlertSubscription)

    if user_identifier:
        query = query.filter(AlertSubscription.user_identifier == user_identifier)

    if area_name:
        query = query.filter(AlertSubscription.area_name == area_name)

    if category:
        query = query.filter(AlertSubscription.category == category)

    if active_only:
        query = query.filter(AlertSubscription.is_active == True)

    return query.offset(skip).limit(limit).all()


@router.delete("/subscriptions/{subscription_id}")
def deactivate_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
):
    subscription = (
        db.query(AlertSubscription)
        .filter(AlertSubscription.id == subscription_id)
        .first()
    )

    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    subscription.is_active = False
    db.commit()

    return {"message": "Subscription deactivated successfully"}


@router.get("/", response_model=list[AlertRecordResponse])
def get_alerts(
    db: Session = Depends(get_db),
    subscription_id: int | None = None,
    unread_only: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    query = db.query(AlertRecord)

    if subscription_id:
        query = query.filter(AlertRecord.subscription_id == subscription_id)

    if unread_only:
        query = query.filter(AlertRecord.is_read == False)

    return query.order_by(AlertRecord.created_at.desc()).offset(skip).limit(limit).all()


@router.patch("/{alert_id}/read", response_model=AlertRecordResponse)
def mark_alert_as_read(
    alert_id: int,
    db: Session = Depends(get_db),
):
    alert = db.query(AlertRecord).filter(AlertRecord.id == alert_id).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.is_read = True

    db.commit()
    db.refresh(alert)

    return alert


@router.post("/generate/{incident_id}", response_model=list[AlertRecordResponse])
def generate_alerts_for_incident(
    incident_id: int,
    db: Session = Depends(get_db),
):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if incident.status != "verified":
        raise HTTPException(
            status_code=400,
            detail="Alerts can only be generated for verified incidents",
        )

    alerts = create_alerts_for_verified_incident(db, incident)

    db.commit()

    for alert in alerts:
        db.refresh(alert)

    return alerts