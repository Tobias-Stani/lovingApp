from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.routers.deps import get_current_user
from app.models.user import User
from app.models.trip import Trip
from app.models.todo import Todo
from app.models.couple import Couple

router = APIRouter(prefix="/api/trips/{trip_id}/todos", tags=["todos"])


class TodoCreate(BaseModel):
    text:     str
    position: Optional[int] = 0


class TodoUpdate(BaseModel):
    text:     Optional[str]  = None
    done:     Optional[bool] = None
    position: Optional[int]  = None


def todo_to_dict(t: Todo) -> dict:
    return {
        "id":       t.id,
        "trip_id":  t.trip_id,
        "text":     t.text,
        "done":     t.done,
        "position": t.position,
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
def list_todos(
    trip_id: int,
    db:      Session = Depends(get_db),
    user:    User    = Depends(get_current_user),
):
    get_trip_or_404(trip_id, user, db)
    todos = db.query(Todo).filter(Todo.trip_id == trip_id).order_by(Todo.position, Todo.id).all()
    return [todo_to_dict(t) for t in todos]


@router.post("/", status_code=201)
def create_todo(
    trip_id: int,
    body:    TodoCreate,
    db:      Session = Depends(get_db),
    user:    User    = Depends(get_current_user),
):
    get_trip_or_404(trip_id, user, db)
    count = db.query(Todo).filter(Todo.trip_id == trip_id).count()
    todo  = Todo(trip_id=trip_id, text=body.text, done=False, position=count)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo_to_dict(todo)


@router.put("/{todo_id}")
def update_todo(
    trip_id: int,
    todo_id: int,
    body:    TodoUpdate,
    db:      Session = Depends(get_db),
    user:    User    = Depends(get_current_user),
):
    get_trip_or_404(trip_id, user, db)
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.trip_id == trip_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo no encontrado")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(todo, field, value)
    db.commit()
    db.refresh(todo)
    return todo_to_dict(todo)


@router.delete("/{todo_id}", status_code=204)
def delete_todo(
    trip_id: int,
    todo_id: int,
    db:      Session = Depends(get_db),
    user:    User    = Depends(get_current_user),
):
    get_trip_or_404(trip_id, user, db)
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.trip_id == trip_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo no encontrado")
    db.delete(todo)
    db.commit()
