from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    completed: Optional[bool] = False

class TaskCreate(TaskBase):
    project_id: int

class TaskUpdate(TaskBase):
    pass

class TaskOut(TaskBase):
    id: int
    created_at: datetime
    owner_id: int
    project_id: int
    class Config:
        from_attributes = True