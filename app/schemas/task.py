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

class TaskCreate(TaskBase):
    project_id: int

class TaskUpdate(TaskBase):
    pass

class TaskOut(TaskBase):
    id: int
    created_at: datetime
    owner_id: int | None = None
    project_id: int | None = None

    priority: Optional[str] = "Low"
    category: Optional[str] = "Personal"

    class Config:
        from_attributes = True