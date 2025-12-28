from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.task import Task
from app.models.project import Project
from app.models.user import User
from app.schemas.task import TaskCreate, TaskOut
from app.oauth2 import get_current_user
from app.services.ai_services import analyze_task_with_ai
from pydantic import BaseModel

router = APIRouter(prefix="/tasks", tags=["tasks"])

class AISentence(BaseModel):
    text: str
    project_id: int

@router.post("/generate", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task_with_ai(
        payload: AISentence,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Takes a sentece ("Buy milk tomorrow")
    analysied by Gemini and creates the task")
    """
    # 1. check the project
    project = db.query(Project).filter(Project.id == payload.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # 2. Ask Gemini
    ai_data = analyze_task_with_ai(payload.text)

    # 3. create the task with the data from Gemini
    new_task = Task(
        title=ai_data.get("summary"),
        description=ai_data.get("description"),
        priority=ai_data.get("priority"),
        category=ai_data.get("category"),
        owner_id=current_user.id,
        project_id=payload.project_id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    # DEBUG PRINT: Sehen wir das Objekt im Log?
    print(f"Task created: {new_task.title}, ID: {new_task.id}")

    # WICHTIG: Das return muss auf der gleichen Höhe sein wie db.refresh!
    return new_task


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