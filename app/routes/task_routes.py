from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.task import Task
from app.models.project import Project
from app.models.user import User
from app.schemas.task import TaskCreate, TaskOut
from app.oauth2 import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])


# 1. Neuen Task erstellen (Geschützt)
@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
        task_data: TaskCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # Prüfen, ob das Projekt existiert und dem User gehört (optional, aber sauber)
    project = db.query(Project).filter(Project.id == task_data.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Task erstellen
    new_task = Task(
        **task_data.dict(),
        owner_id=current_user.id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


# 2. Alle Tasks des eingeloggten Users lesen
@router.get("/", response_model=List[TaskOut])
def get_my_tasks(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # Nur Tasks zurückgeben, die MIR gehören
    tasks = db.query(Task).filter(Task.owner_id == current_user.id).all()
    return tasks


# 3. Einen spezifischen Task löschen
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
        task_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    task_query = db.query(Task).filter(Task.id == task_id)
    task = task_query.first()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    # Sicherheits-Check: Gehört der Task mir?
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this task")

    task_query.delete(synchronize_session=False)
    db.commit()
    return