from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class DateEntry(Base):
    __tablename__ = "date_entries"

    id            = Column(Integer, primary_key=True, index=True)
    couple_id     = Column(Integer, ForeignKey("couples.id"), nullable=False)
    title         = Column(String(200), nullable=False)
    description   = Column(Text, nullable=True)
    location_name = Column(String(200), nullable=True)
    maps_url      = Column(String(1000), nullable=True)
    date_occurred = Column(Date, nullable=False)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

    couple     = relationship("Couple")
    photos     = relationship("DatePhoto", back_populates="date_entry", cascade="all, delete-orphan", order_by="DatePhoto.position")
    activities = relationship("DateActivity", back_populates="date_entry", cascade="all, delete-orphan", order_by="DateActivity.position")
