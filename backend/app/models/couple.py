from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Couple(Base):
    """
    Representa una conexión entre dos usuarios.
    - requester_id: quien envió la invitación
    - receiver_id:  quien la recibió
    - status:       'pending' | 'accepted' | 'rejected'
    Una vez aceptada, ambos comparten viajes.
    Solo puede existir una fila activa (pending o accepted) por par de usuarios.
    """
    __tablename__ = "couples"

    id           = Column(Integer, primary_key=True, index=True)
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id  = Column(Integer, ForeignKey("users.id"), nullable=False)
    status       = Column(String(20), nullable=False, default="pending")
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
    updated_at   = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    requester = relationship("User", foreign_keys=[requester_id], back_populates="sent_invitations")
    receiver  = relationship("User", foreign_keys=[receiver_id],  back_populates="received_invitations")
