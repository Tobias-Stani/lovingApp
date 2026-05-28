from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel
from typing import Optional, Literal
from app.core.database import get_db
from app.routers.deps import get_current_user
from app.models.user import User
from app.models.trip import Trip
from app.models.place import Place
from app.models.couple import Couple

router = APIRouter(prefix="/api/trips/{trip_id}/places", tags=["places"])

PlaceType = Literal["restaurant", "hotel", "attraction", "activity", "other"]


class PlaceCreate(BaseModel):
    name:     str
    type:     PlaceType = "other"
    notes:    Optional[str] = None
    maps_url: Optional[str] = None


class PlaceUpdate(BaseModel):
    name:     Optional[str] = None
    type:     Optional[PlaceType] = None
    notes:    Optional[str] = None
    maps_url: Optional[str] = None


def place_to_dict(p: Place) -> dict:
    return {
        "id":         p.id,
        "trip_id":    p.trip_id,
        "name":       p.name,
        "type":       p.type,
        "notes":      p.notes,
        "maps_url":   p.maps_url,
        "created_at": p.created_at.isoformat(),
    }


def _partner_id(user_id: int, db: Session):
    row = db.query(Couple).filter(
        or_(Couple.requester_id == user_id, Couple.receiver_id == user_id),
        Couple.status == "accepted",
    ).first()
    if not row:
        return None
    return row.receiver_id if row.requester_id == user_id else row.requester_id


def get_trip_or_404(trip_id: int, user: User, db: Session) -> Trip:
    partner_id = _partner_id(user.id, db)
    owner_ids  = [user.id] + ([partner_id] if partner_id else [])
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.owner_id.in_(owner_ids)).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    return trip


@router.get("/")
def list_places(
    trip_id: int,
    db:   Session = Depends(get_db),
    user: User    = Depends(get_current_user),
):
    get_trip_or_404(trip_id, user, db)
    places = db.query(Place).filter(Place.trip_id == trip_id).order_by(Place.created_at).all()
    return [place_to_dict(p) for p in places]


@router.post("/", status_code=201)
def create_place(
    trip_id: int,
    body:    PlaceCreate,
    db:      Session = Depends(get_db),
    user:    User    = Depends(get_current_user),
):
    get_trip_or_404(trip_id, user, db)
    place = Place(trip_id=trip_id, **body.model_dump())
    db.add(place)
    db.commit()
    db.refresh(place)
    return place_to_dict(place)


@router.put("/{place_id}")
def update_place(
    trip_id:  int,
    place_id: int,
    body:     PlaceUpdate,
    db:       Session = Depends(get_db),
    user:     User    = Depends(get_current_user),
):
    get_trip_or_404(trip_id, user, db)
    place = db.query(Place).filter(Place.id == place_id, Place.trip_id == trip_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Lugar no encontrado")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(place, field, value)
    db.commit()
    db.refresh(place)
    return place_to_dict(place)


@router.delete("/{place_id}", status_code=204)
def delete_place(
    trip_id:  int,
    place_id: int,
    db:       Session = Depends(get_db),
    user:     User    = Depends(get_current_user),
):
    get_trip_or_404(trip_id, user, db)
    place = db.query(Place).filter(Place.id == place_id, Place.trip_id == trip_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Lugar no encontrado")
    db.delete(place)
    db.commit()
