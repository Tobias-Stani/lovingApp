from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class DatePhoto(Base):
    __tablename__ = "date_photos"

    id          = Column(Integer, primary_key=True, index=True)
    date_id     = Column(Integer, ForeignKey("date_entries.id"), nullable=False)
    image_data  = Column(LargeBinary, nullable=False)
    thumbnail   = Column(LargeBinary, nullable=True)
    caption     = Column(String(500), nullable=True)
    mime_type   = Column(String(50), nullable=False, default="image/jpeg")
    position    = Column(Integer, default=0, nullable=False)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    date_entry = relationship("DateEntry", back_populates="photos")
