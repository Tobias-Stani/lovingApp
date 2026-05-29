from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class TripCreate(BaseModel):
    destination: str
    country: Optional[str] = None
    departure_date: date
    return_date: Optional[date] = None
    description: Optional[str] = None
    cover_emoji: Optional[str] = "✈️"
    accommodation_name: Optional[str] = None
    accommodation_maps_url: Optional[str] = None
    accommodation_checkin: Optional[date] = None
    accommodation_checkout: Optional[date] = None
    accommodation_notes: Optional[str] = None


class TripUpdate(BaseModel):
    destination: Optional[str] = None
    country: Optional[str] = None
    departure_date: Optional[date] = None
    return_date: Optional[date] = None
    description: Optional[str] = None
    cover_emoji: Optional[str] = None
    accommodation_name: Optional[str] = None
    accommodation_maps_url: Optional[str] = None
    accommodation_checkin: Optional[date] = None
    accommodation_checkout: Optional[date] = None
    accommodation_notes: Optional[str] = None


class TripOut(BaseModel):
    id: int
    destination: str
    country: Optional[str]
    departure_date: date
    return_date: Optional[date]
    description: Optional[str]
    cover_emoji: Optional[str]
    owner_id: int
    created_at: datetime
    accommodation_name: Optional[str] = None
    accommodation_maps_url: Optional[str] = None
    accommodation_checkin: Optional[date] = None
    accommodation_checkout: Optional[date] = None
    accommodation_notes: Optional[str] = None

    class Config:
        from_attributes = True
