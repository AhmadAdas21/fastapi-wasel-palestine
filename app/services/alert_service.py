from math import radians, sin, cos, sqrt, atan2

from sqlalchemy.orm import Session

from app.models.alert import AlertSubscription, AlertRecord


def calculate_distance_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    earth_radius_km = 6371.0

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return earth_radius_km * c


def create_alerts_for_verified_incident(db: Session, incident):
    subscriptions = (
        db.query(AlertSubscription)
        .filter(AlertSubscription.is_active == True)
        .all()
    )

    created_alerts = []

    for subscription in subscriptions:
        if subscription.category and subscription.category != incident.category:
            continue

        distance = calculate_distance_km(
            subscription.latitude,
            subscription.longitude,
            incident.latitude,
            incident.longitude,
        )

        if distance <= subscription.radius_km:
            alert = AlertRecord(
                subscription_id=subscription.id,
                incident_id=incident.id,
                title=f"New verified incident: {incident.category}",
                message=f"{incident.title} near {subscription.area_name}. Distance: {round(distance, 2)} km",
            )

            db.add(alert)
            created_alerts.append(alert)

    return created_alerts