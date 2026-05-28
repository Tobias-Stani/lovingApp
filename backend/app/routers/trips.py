from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import date
from app.core.database import get_db
from app.routers.deps import get_current_user
from app.models.user import User
from app.models.trip import Trip
from app.models.couple import Couple
from app.schemas.trip import TripCreate, TripUpdate

router = APIRouter(prefix="/api/trips", tags=["trips"])


def _partner_id(user_id: int, db: Session):
    """Retorna el id del partner si tienen pareja aceptada, sino None."""
    row = db.query(Couple).filter(
        or_(
            Couple.requester_id == user_id,
            Couple.receiver_id  == user_id,
        ),
        Couple.status == "accepted",
    ).first()
    if not row:
        return None
    return row.receiver_id if row.requester_id == user_id else row.requester_id


def trip_to_dict(trip: Trip) -> dict:
    today = date.today()
    days_left = (trip.departure_date - today).days
    return {
        "id":             trip.id,
        "destination":    trip.destination,
        "country":        trip.country,
        "departure_date": trip.departure_date.isoformat(),
        "return_date":    trip.return_date.isoformat() if trip.return_date else None,
        "description":    trip.description,
        "cover_emoji":    trip.cover_emoji,
        "owner_id":       trip.owner_id,
        "created_at":     trip.created_at.isoformat(),
        "days_left":      days_left,
    }


@router.get("/")
def list_trips(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    partner_id = _partner_id(current_user.id, db)
    owner_ids  = [current_user.id] + ([partner_id] if partner_id else [])
    trips = (
        db.query(Trip)
        .filter(Trip.owner_id.in_(owner_ids))
        .order_by(Trip.departure_date)
        .all()
    )
    return [trip_to_dict(t) for t in trips]


@router.post("/", status_code=201)
def create_trip(
    body: TripCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = Trip(**body.model_dump(), owner_id=current_user.id)
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip_to_dict(trip)


@router.get("/{trip_id}")
def get_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    partner_id = _partner_id(current_user.id, db)
    owner_ids  = [current_user.id] + ([partner_id] if partner_id else [])
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.owner_id.in_(owner_ids)).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    return trip_to_dict(trip)


@router.put("/{trip_id}")
def update_trip(
    trip_id: int,
    body: TripUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    partner_id = _partner_id(current_user.id, db)
    owner_ids  = [current_user.id] + ([partner_id] if partner_id else [])
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.owner_id.in_(owner_ids)).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(trip, field, value)
    db.commit()
    db.refresh(trip)
    return trip_to_dict(trip)


@router.delete("/{trip_id}", status_code=204)
def delete_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    partner_id = _partner_id(current_user.id, db)
    owner_ids  = [current_user.id] + ([partner_id] if partner_id else [])
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.owner_id.in_(owner_ids)).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    db.delete(trip)
    db.commit()
