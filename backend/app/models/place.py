from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Place(Base):
    __tablename__ = "places"

    id         = Column(Integer, primary_key=True, index=True)
    trip_id    = Column(Integer, ForeignKey("trips.id"), nullable=False)
    name       = Column(String(200), nullable=False)
    # restaurant | hotel | attraction | activity | other
    type       = Column(String(50), nullable=False, default="other")
    notes      = Column(Text, nullable=True)
    maps_url   = Column(String(1000), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    trip = relationship("Trip", back_populates="places")
