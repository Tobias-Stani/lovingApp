from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    destination = Column(String(150), nullable=False)
    country = Column(String(100), nullable=True)
    departure_date = Column(Date, nullable=False)
    return_date = Column(Date, nullable=True)
    description = Column(Text, nullable=True)
    cover_emoji = Column(String(10), nullable=True, default="✈️")
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    accommodation_name      = Column(String(200), nullable=True)
    accommodation_maps_url  = Column(Text, nullable=True)
    accommodation_checkin   = Column(Date, nullable=True)
    accommodation_checkout  = Column(Date, nullable=True)
    accommodation_notes     = Column(Text, nullable=True)

    deleted_at = Column(DateTime(timezone=True), nullable=True, default=None)

    owner  = relationship("User", back_populates="trips")
    places = relationship("Place", back_populates="trip", cascade="all, delete-orphan", order_by="Place.created_at")
