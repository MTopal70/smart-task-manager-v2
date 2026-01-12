# app/schemas/task.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    completed: Optional[bool] = False
    priority: Optional[str] = "Medium"
    category: Optional[str] = "General"

    # --- WICHTIG: Diese Felder haben gefehlt ---
    status: Optional[str] = "todo"
    is_locked: Optional[bool] = False
    # -------------------------------------------


class TaskCreate(TaskBase):
    project_id: int


class TaskUpdate(BaseModel):
    # Wir nutzen hier BaseModel statt TaskBase, damit beim Update
    # alle Felder optional sind (auch der Title).
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    completed: Optional[bool] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    is_locked: Optional[bool] = None


class TaskOut(TaskBase):
    id: int
    created_at: datetime
    owner_id: int | None = None
    project_id: int | None = None

    # Falls du hier Defaults überschreiben wolltest, ist das okay,
    # aber eigentlich kommen die Werte jetzt aus TaskBase/DB.
    # priority: Optional[str] = "Low"
    # category: Optional[str] = "Personal"

    class Config:
        from_attributes = True