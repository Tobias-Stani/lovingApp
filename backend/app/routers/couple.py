from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from pydantic import BaseModel
from app.core.database import get_db
from app.routers.deps import get_current_user
from app.models.user import User
from app.models.couple import Couple

router = APIRouter(prefix="/api/couple", tags=["couple"])


# ── helpers ───────────────────────────────────────────────

def _active_couple(user_id: int, db: Session):
    """Retorna la fila Couple activa (pending o accepted) para el usuario, o None."""
    return db.query(Couple).filter(
        or_(
            Couple.requester_id == user_id,
            Couple.receiver_id  == user_id,
        ),
        Couple.status.in_(["pending", "accepted"]),
    ).first()


def _user_to_dict(u: User) -> dict:
    return {
        "id":        u.id,
        "username":  u.username,
        "full_name": u.full_name,
        "avatar_url": u.avatar_url,
    }


def couple_status_for(user: User, db: Session) -> dict:
    """
    Devuelve el estado de la pareja del usuario:
    {
      "status": "none" | "pending_sent" | "pending_received" | "accepted",
      "couple_id": int | None,
      "partner": {...} | None,
    }
    """
    row = _active_couple(user.id, db)
    if not row:
        return {"status": "none", "couple_id": None, "partner": None}

    is_requester = row.requester_id == user.id
    partner_obj  = row.receiver if is_requester else row.requester

    if row.status == "accepted":
        return {"status": "accepted", "couple_id": row.id, "partner": _user_to_dict(partner_obj)}

    # pending
    if is_requester:
        return {"status": "pending_sent", "couple_id": row.id, "partner": _user_to_dict(partner_obj)}
    else:
        return {"status": "pending_received", "couple_id": row.id, "partner": _user_to_dict(partner_obj)}


# ── rutas ─────────────────────────────────────────────────

@router.get("/status")
def get_status(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return couple_status_for(user, db)


class InviteRequest(BaseModel):
    username: str


@router.post("/invite")
def invite(body: InviteRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if body.username == user.username:
        raise HTTPException(status_code=400, detail="No podés invitarte a vos mismo")

    # verificar que el invitante no tenga pareja activa
    if _active_couple(user.id, db):
        raise HTTPException(status_code=400, detail="Ya tenés una invitación o pareja activa")

    target = db.query(User).filter(User.username == body.username).first()
    if not target:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # verificar que el destinatario no tenga pareja activa
    if _active_couple(target.id, db):
        raise HTTPException(status_code=400, detail="Ese usuario ya tiene una pareja o invitación pendiente")

    couple = Couple(requester_id=user.id, receiver_id=target.id, status="pending")
    db.add(couple)
    db.commit()
    db.refresh(couple)
    return couple_status_for(user, db)


@router.post("/accept")
def accept(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = db.query(Couple).filter(
        Couple.receiver_id == user.id,
        Couple.status == "pending",
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="No hay invitación pendiente para aceptar")
    row.status = "accepted"
    db.commit()
    return couple_status_for(user, db)


@router.post("/reject")
def reject(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = db.query(Couple).filter(
        Couple.receiver_id == user.id,
        Couple.status == "pending",
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="No hay invitación pendiente para rechazar")
    db.delete(row)
    db.commit()
    return {"status": "none", "couple_id": None, "partner": None}


@router.post("/cancel")
def cancel(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Cancela una invitación enviada aún pendiente."""
    row = db.query(Couple).filter(
        Couple.requester_id == user.id,
        Couple.status == "pending",
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="No hay invitación pendiente para cancelar")
    db.delete(row)
    db.commit()
    return {"status": "none", "couple_id": None, "partner": None}


@router.post("/unlink")
def unlink(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Desvincula una pareja aceptada."""
    row = db.query(Couple).filter(
        or_(
            Couple.requester_id == user.id,
            Couple.receiver_id  == user.id,
        ),
        Couple.status == "accepted",
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="No tenés pareja vinculada")
    db.delete(row)
    db.commit()
    return {"status": "none", "couple_id": None, "partner": None}
