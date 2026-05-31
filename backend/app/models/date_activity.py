from sqlalchemy import Column, Integer, String, Text, Time, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class DateActivity(Base):
    __tablename__ = "date_activities"

    id          = Column(Integer, primary_key=True, index=True)
    date_id     = Column(Integer, ForeignKey("date_entries.id"), nullable=False)
    title       = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    time_at     = Column(Time, nullable=True)
    position    = Column(Integer, default=0, nullable=False)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    date_entry = relationship("DateEntry", back_populates="activities")
