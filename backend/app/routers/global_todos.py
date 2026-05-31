from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.routers.deps import get_current_user
from app.models.user import User
from app.models.global_todo import GlobalTodo
from app.models.couple import Couple

router = APIRouter(prefix="/api/todos", tags=["global-todos"])


class TodoCreate(BaseModel):
    text: str


class TodoUpdate(BaseModel):
    text:     Optional[str]  = None
    done:     Optional[bool] = None
    position: Optional[int]  = None


def _partner_id(user_id: int, db: Session):
    row = db.query(Couple).filter(
        or_(Couple.requester_id == user_id, Couple.receiver_id == user_id),
        Couple.status == "accepted",
    ).first()
    if not row:
        return None
    return row.receiver_id if row.requester_id == user_id else row.requester_id


def todo_to_dict(t: GlobalTodo) -> dict:
    return {
        "id":       t.id,
        "owner_id": t.owner_id,
        "text":     t.text,
        "done":     t.done,
        "position": t.position,
    }


@router.get("/")
def list_todos(
    db:   Session = Depends(get_db),
    user: User    = Depends(get_current_user),
):
    partner_id = _partner_id(user.id, db)
    owner_ids  = [user.id] + ([partner_id] if partner_id else [])
    todos = db.query(GlobalTodo).filter(
        GlobalTodo.owner_id.in_(owner_ids)
    ).order_by(GlobalTodo.position, GlobalTodo.id).all()
    return [todo_to_dict(t) for t in todos]


@router.post("/", status_code=201)
def create_todo(
    body: TodoCreate,
    db:   Session = Depends(get_db),
    user: User    = Depends(get_current_user),
):
    count = db.query(GlobalTodo).filter(GlobalTodo.owner_id == user.id).count()
    todo  = GlobalTodo(owner_id=user.id, text=body.text, done=False, position=count)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo_to_dict(todo)


@router.put("/{todo_id}")
def update_todo(
    todo_id: int,
    body:    TodoUpdate,
    db:      Session = Depends(get_db),
    user:    User    = Depends(get_current_user),
):
    partner_id = _partner_id(user.id, db)
    owner_ids  = [user.id] + ([partner_id] if partner_id else [])
    todo = db.query(GlobalTodo).filter(
        GlobalTodo.id == todo_id, GlobalTodo.owner_id.in_(owner_ids)
    ).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo no encontrado")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(todo, field, value)
    db.commit()
    db.refresh(todo)
    return todo_to_dict(todo)


@router.delete("/{todo_id}", status_code=204)
def delete_todo(
    todo_id: int,
    db:      Session = Depends(get_db),
    user:    User    = Depends(get_current_user),
):
    partner_id = _partner_id(user.id, db)
    owner_ids  = [user.id] + ([partner_id] if partner_id else [])
    todo = db.query(GlobalTodo).filter(
        GlobalTodo.id == todo_id, GlobalTodo.owner_id.in_(owner_ids)
    ).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo no encontrado")
    db.delete(todo)
    db.commit()
