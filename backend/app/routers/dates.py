import io
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel
from typing import List
from app.core.database import get_db
from app.routers.deps import get_current_user
from app.models.user import User
from app.models.couple import Couple
from app.models.date_entry import DateEntry
from app.models.date_photo import DatePhoto
from app.models.date_activity import DateActivity
from fastapi.responses import Response

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

router = APIRouter(prefix="/api/dates", tags=["dates"])

MAX_IMAGE_SIZE = 20 * 1024 * 1024
MAX_IMAGE_DIM = 2000
THUMB_WIDTH = 400


def _active_couple(user_id: int, db: Session):
    return db.query(Couple).filter(
        or_(Couple.requester_id == user_id, Couple.receiver_id == user_id),
        Couple.status == "accepted",
    ).first()


def _make_thumbnail(data: bytes, mime: str) -> Optional[bytes]:
    if not HAS_PIL:
        return None
    try:
        img = Image.open(io.BytesIO(data))
        img.thumbnail((THUMB_WIDTH, THUMB_WIDTH))
        fmt = "JPEG" if mime == "image/jpeg" else "PNG"
        buf = io.BytesIO()
        img.save(buf, format=fmt, quality=75)
        return buf.getvalue()
    except Exception:
        return None


def _downscale_if_needed(data: bytes, mime: str) -> bytes:
    if not HAS_PIL:
        return data
    try:
        img = Image.open(io.BytesIO(data))
        if img.width <= MAX_IMAGE_DIM and img.height <= MAX_IMAGE_DIM:
            return data
        img.thumbnail((MAX_IMAGE_DIM, MAX_IMAGE_DIM), Image.LANCZOS)
        fmt = "JPEG" if mime in ("image/jpeg", "image/jpg") else "PNG"
        buf = io.BytesIO()
        img.save(buf, format=fmt, quality=85, optimize=True)
        return buf.getvalue()
    except Exception:
        return data


def date_entry_to_dict(d: DateEntry) -> dict:
    photos     = d.photos or []
    activities = d.activities or []
    return {
        "id": d.id,
        "couple_id": d.couple_id,
        "title": d.title,
        "description": d.description,
        "location_name": d.location_name,
        "maps_url": d.maps_url,
        "date_occurred": d.date_occurred.isoformat(),
        "created_at": d.created_at.isoformat() if d.created_at else None,
        "photos": [photo_to_dict(p) for p in photos],
        "photo_count": len(photos),
        "activities": [activity_to_dict(a) for a in activities],
        "activity_count": len(activities),
    }


def activity_to_dict(a: DateActivity) -> dict:
    return {
        "id": a.id,
        "date_id": a.date_id,
        "title": a.title,
        "description": a.description,
        "time_at": a.time_at.isoformat()[:5] if a.time_at else None,
        "position": a.position,
    }


def photo_to_dict(p: DatePhoto) -> dict:
    return {
        "id": p.id,
        "caption": p.caption,
        "mime_type": p.mime_type,
        "position": p.position,
    }


@router.get("/")
def list_dates(
    db:   Session = Depends(get_db),
    user: User    = Depends(get_current_user),
):
    couple = _active_couple(user.id, db)
    if not couple:
        return []
    dates = db.query(DateEntry).filter(
        DateEntry.couple_id == couple.id
    ).order_by(DateEntry.date_occurred.desc(), DateEntry.created_at.desc()).all()
    return [date_entry_to_dict(d) for d in dates]


@router.post("/", status_code=201)
def create_date(
    title: str = Form(...),
    date_occurred: str = Form(...),
    description: Optional[str] = Form(None),
    location_name: Optional[str] = Form(None),
    maps_url: Optional[str] = Form(None),
    photos: list[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    couple = _active_couple(user.id, db)
    if not couple:
        raise HTTPException(status_code=400, detail="Necesitás tener pareja para crear recuerdos")

    try:
        parsed_date = date.fromisoformat(date_occurred)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido (YYYY-MM-DD)")

    entry = DateEntry(
        couple_id=couple.id,
        title=title,
        description=description,
        location_name=location_name,
        maps_url=maps_url,
        date_occurred=parsed_date,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    for i, f in enumerate(photos):
        if not f.filename:
            continue
        data = f.file.read()
        if len(data) > MAX_IMAGE_SIZE:
            continue
        mime = f.content_type or "image/jpeg"
        data = _downscale_if_needed(data, mime)
        thumb = _make_thumbnail(data, mime)
        photo = DatePhoto(
            date_id=entry.id,
            image_data=data,
            thumbnail=thumb,
            mime_type=mime,
            position=i,
        )
        db.add(photo)

    db.commit()
    db.refresh(entry)
    return date_entry_to_dict(entry)


@router.get("/{date_id}")
def get_date(
    date_id: int,
    db:  Session = Depends(get_db),
    user: User   = Depends(get_current_user),
):
    couple = _active_couple(user.id, db)
    if not couple:
        raise HTTPException(status_code=404, detail="Recuerdo no encontrado")
    entry = db.query(DateEntry).filter(
        DateEntry.id == date_id,
        DateEntry.couple_id == couple.id,
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Recuerdo no encontrado")
    return date_entry_to_dict(entry)


@router.put("/{date_id}")
def update_date(
    date_id: int,
    title: Optional[str] = Form(None),
    date_occurred: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    location_name: Optional[str] = Form(None),
    maps_url: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    couple = _active_couple(user.id, db)
    if not couple:
        raise HTTPException(status_code=404, detail="Recuerdo no encontrado")
    entry = db.query(DateEntry).filter(
        DateEntry.id == date_id,
        DateEntry.couple_id == couple.id,
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Recuerdo no encontrado")

    if title is not None:
        entry.title = title
    if date_occurred is not None:
        try:
            entry.date_occurred = date.fromisoformat(date_occurred)
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido")
    if description is not None:
        entry.description = description
    if location_name is not None:
        entry.location_name = location_name
    if maps_url is not None:
        entry.maps_url = maps_url

    db.commit()
    db.refresh(entry)
    return date_entry_to_dict(entry)


@router.delete("/{date_id}", status_code=204)
def delete_date(
    date_id: int,
    db:  Session = Depends(get_db),
    user: User   = Depends(get_current_user),
):
    couple = _active_couple(user.id, db)
    if not couple:
        raise HTTPException(status_code=404, detail="Recuerdo no encontrado")
    entry = db.query(DateEntry).filter(
        DateEntry.id == date_id,
        DateEntry.couple_id == couple.id,
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Recuerdo no encontrado")
    db.delete(entry)
    db.commit()


@router.post("/{date_id}/photos", status_code=201)
def add_photos(
    date_id: int,
    photos: list[UploadFile] = File(...),
    db:  Session = Depends(get_db),
    user: User   = Depends(get_current_user),
):
    couple = _active_couple(user.id, db)
    if not couple:
        raise HTTPException(status_code=404, detail="Recuerdo no encontrado")
    entry = db.query(DateEntry).filter(
        DateEntry.id == date_id,
        DateEntry.couple_id == couple.id,
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Recuerdo no encontrado")

    max_pos = db.query(DatePhoto.position).filter(
        DatePhoto.date_id == entry.id
    ).order_by(DatePhoto.position.desc()).first()
    next_pos = (max_pos[0] + 1) if max_pos else 0

    added = []
    for i, f in enumerate(photos):
        if not f.filename:
            continue
        data = f.file.read()
        if len(data) > MAX_IMAGE_SIZE:
            continue
        mime = f.content_type or "image/jpeg"
        data = _downscale_if_needed(data, mime)
        thumb = _make_thumbnail(data, mime)
        photo = DatePhoto(
            date_id=entry.id,
            image_data=data,
            thumbnail=thumb,
            mime_type=mime,
            position=next_pos + i,
        )
        db.add(photo)
        db.flush()
        added.append(photo)

    db.commit()
    return [photo_to_dict(p) for p in added]


@router.get("/photos/{photo_id}/image")
def get_photo_image(
    photo_id: int,
    thumbnail: bool = Query(False),
    db:  Session = Depends(get_db),
    user: User   = Depends(get_current_user),
):
    couple = _active_couple(user.id, db)
    if not couple:
        raise HTTPException(status_code=404, detail="Foto no encontrada")
    photo = db.query(DatePhoto).join(DateEntry).filter(
        DatePhoto.id == photo_id,
        DateEntry.couple_id == couple.id,
    ).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Foto no encontrada")

    data = photo.thumbnail if (thumbnail and photo.thumbnail) else photo.image_data
    return Response(content=data, media_type=photo.mime_type)


@router.delete("/photos/{photo_id}", status_code=204)
def delete_photo(
    photo_id: int,
    db:  Session = Depends(get_db),
    user: User   = Depends(get_current_user),
):
    couple = _active_couple(user.id, db)
    if not couple:
        raise HTTPException(status_code=404, detail="Foto no encontrada")
    photo = db.query(DatePhoto).join(DateEntry).filter(
        DatePhoto.id == photo_id,
        DateEntry.couple_id == couple.id,
    ).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Foto no encontrada")
    db.delete(photo)
    db.commit()


class ReorderActivitiesRequest(BaseModel):
    date_id: int
    activity_ids: List[int]


def _get_date_entry(date_id: int, couple_id: int, db: Session):
    return db.query(DateEntry).filter(
        DateEntry.id == date_id,
        DateEntry.couple_id == couple_id,
    ).first()


@router.put("/activities/reorder")
def reorder_activities(
    body: ReorderActivitiesRequest,
    db:  Session = Depends(get_db),
    user: User   = Depends(get_current_user),
):
    couple = _active_couple(user.id, db)
    if not couple:
        raise HTTPException(status_code=404, detail="Date no encontrada")
    entry = _get_date_entry(body.date_id, couple.id, db)
    if not entry:
        raise HTTPException(status_code=404, detail="Date no encontrada")

    for pos, act_id in enumerate(body.activity_ids):
        act = db.query(DateActivity).filter(
            DateActivity.id == act_id,
            DateActivity.date_id == entry.id,
        ).first()
        if act:
            act.position = pos
    db.commit()
    return {"ok": True}


@router.get("/{date_id}/activities")
def list_activities(
    date_id: int,
    db:  Session = Depends(get_db),
    user: User   = Depends(get_current_user),
):
    couple = _active_couple(user.id, db)
    if not couple:
        raise HTTPException(status_code=404, detail="Date no encontrada")
    entry = _get_date_entry(date_id, couple.id, db)
    if not entry:
        raise HTTPException(status_code=404, detail="Date no encontrada")
    return [activity_to_dict(a) for a in (entry.activities or [])]


@router.post("/{date_id}/activities", status_code=201)
def create_activity(
    date_id: int,
    title: str = Form(...),
    description: Optional[str] = Form(None),
    time_at: Optional[str] = Form(None),
    db:  Session = Depends(get_db),
    user: User   = Depends(get_current_user),
):
    couple = _active_couple(user.id, db)
    if not couple:
        raise HTTPException(status_code=404, detail="Date no encontrada")
    entry = _get_date_entry(date_id, couple.id, db)
    if not entry:
        raise HTTPException(status_code=404, detail="Date no encontrada")

    parsed_time = None
    if time_at:
        try:
            from datetime import time
            h, m = time_at.split(":")
            parsed_time = time(int(h), int(m))
        except Exception:
            raise HTTPException(status_code=400, detail="Formato de hora inválido (HH:MM)")

    count = len(entry.activities or [])
    act = DateActivity(
        date_id=entry.id,
        title=title,
        description=description,
        time_at=parsed_time,
        position=count,
    )
    db.add(act)
    db.commit()
    db.refresh(act)
    return activity_to_dict(act)


@router.put("/activities/{activity_id}")
def update_activity(
    activity_id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    time_at: Optional[str] = Form(None),
    db:  Session = Depends(get_db),
    user: User   = Depends(get_current_user),
):
    couple = _active_couple(user.id, db)
    if not couple:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")
    act = db.query(DateActivity).join(DateEntry).filter(
        DateActivity.id == activity_id,
        DateEntry.couple_id == couple.id,
    ).first()
    if not act:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")

    if title is not None:
        act.title = title
    if description is not None:
        act.description = description
    if time_at is not None:
        try:
            from datetime import time
            h, m = time_at.split(":")
            act.time_at = time(int(h), int(m))
        except Exception:
            raise HTTPException(status_code=400, detail="Formato de hora inválido")

    db.commit()
    db.refresh(act)
    return activity_to_dict(act)


@router.delete("/activities/{activity_id}", status_code=204)
def delete_activity(
    activity_id: int,
    db:  Session = Depends(get_db),
    user: User   = Depends(get_current_user),
):
    couple = _active_couple(user.id, db)
    if not couple:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")
    act = db.query(DateActivity).join(DateEntry).filter(
        DateActivity.id == activity_id,
        DateEntry.couple_id == couple.id,
    ).first()
    if not act:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")
    db.delete(act)
    db.commit()
