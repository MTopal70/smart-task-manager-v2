from fastapi import APIRouter, Depends, Form, Request, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from starlette.responses import RedirectResponse, JSONResponse  # <--- WICHTIG: JSONResponse hat gefehlt

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


# =================================================================
# 1. HILFSFUNKTIONEN (Für Web-Session Handling)
# =================================================================

def get_local_user_from_session(request: Request, db: Session):
    """
    Holt den User aus der Datenbank basierend auf der Auth0 Browser-Session.
    """
    auth0_user = request.session.get('user')
    if not auth0_user:
        return None

    # Wir suchen den User über die Email (die von Auth0 kommt)
    user_email = auth0_user.get('email')
    if not user_email:
        return None

    return db.query(User).filter(User.email == user_email).first()


# =================================================================
# 2. WEB ROUTES (Für dein HTML Frontend / Browser)
# Diese Routen nutzen Cookies (Sessions) und Form-Data
# =================================================================

# --- A. Drag & Drop Status Update ---
# app/routes/task_routes.py

# Suche nach: @router.post("/{task_id}/move")
# app/routes/task_routes.py

# Suche nach: @router.post("/{task_id}/move")
@router.post("/{task_id}/move")
async def move_task_web(
        task_id: int,
        status: str = Form(...),
        request: Request = None,
        db: Session = Depends(get_db)
):
    # 1. Validierung
    user = get_local_user_from_session(request, db)
    if not user: return JSONResponse({"error": "Unauthorized"}, status_code=401)

    task = db.query(Task).filter(Task.id == task_id).first()
    if not task: return JSONResponse({"error": "Task not found"}, status_code=404)
    if task.owner_id != user.id: return JSONResponse({"error": "Forbidden"}, status_code=403)

    # 2. Status säubern
    clean_status = status.strip().lower()

    # 3. Zuweisen
    task.status = clean_status

    # 4. DIE LOGIK (Jetzt wird sie funktionieren!)
    if clean_status == "done":
        print(f"Task {task_id} -> DONE. Sperre zu.") # Kleiner Print zur Sicherheit
        task.is_locked = True
        task.completed = True
    else:
        print(f"Task {task_id} -> {clean_status}. Sperre auf.")
        task.is_locked = False
        task.completed = False

    # 5. Speichern
    db.commit()
    db.refresh(task)

    # 6. Antwort mit Lock-Status
    return JSONResponse({
        "success": True,
        "new_status": task.status,
        "is_locked": task.is_locked
    })

# --- B. Task Bearbeiten (Titel/Beschreibung) ---
@router.post("/{task_id}/update")
async def update_task_web(
        task_id: int,
        title: str = Form(...),
        description: str = Form(None),
        priority: str = Form(...),
        request: Request = None,
        db: Session = Depends(get_db)
):
    user = get_local_user_from_session(request, db)
    if not user: return RedirectResponse(url="/login", status_code=303)

    task = db.query(Task).filter(Task.id == task_id).first()

    # Sicherheits-Check
    if not task or task.owner_id != user.id:
        return RedirectResponse(url="/", status_code=303)

    # Update
    task.title = title
    task.description = description
    task.priority = priority
    db.commit()

    # Zurück zum Board des Projekts
    return RedirectResponse(url=f"/projects/{task.project_id}/board", status_code=303)


# --- C. Task Löschen ---
@router.post("/{task_id}/delete")
async def delete_task_web(
        task_id: int,
        request: Request,
        db: Session = Depends(get_db)
):
    user = get_local_user_from_session(request, db)
    if not user: return RedirectResponse(url="/login", status_code=303)

    task = db.query(Task).filter(Task.id == task_id).first()

    # Sicherheits-Check
    if not task or task.owner_id != user.id:
        return RedirectResponse(url="/", status_code=303)

    # Projekt ID merken für den Redirect
    redir_project_id = task.project_id

    db.delete(task)
    db.commit()

    if redir_project_id:
        return RedirectResponse(url=f"/projects/{redir_project_id}/board", status_code=303)
    else:
        return RedirectResponse(url="/", status_code=303)


# --- D. KI Generierung über Web Formular ---
@router.post("/generate_web")
async def create_task_ai_web(
        request: Request,
        description: str = Form(...),
        db: Session = Depends(get_db)
):
    user = get_local_user_from_session(request, db)
    if not user: return RedirectResponse(url="/login", status_code=303)

    # KI fragen
    ai_data = analyze_task_with_ai(description)

    # Task speichern
    new_task = Task(
        title=ai_data.get("summary", "Neuer Task"),
        description=ai_data.get("description", ""),
        priority=ai_data.get("priority", "Mittel"),
        category=ai_data.get("category", "General"),
        owner_id=user.id,
        project_id=None  # Vorerst ohne Projekt, oder man übergibt es im Formular
    )

    db.add(new_task)
    db.commit()

    return RedirectResponse(url="/", status_code=303)


# =================================================================
# 3. API ROUTES (Für Mobile Apps / Externe Clients)
# Diese Routen nutzen Bearer Token Auth (get_current_user)
# =================================================================

@router.post("/generate", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task_with_ai_api(
        payload: AISentence,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == payload.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    ai_data = analyze_task_with_ai(payload.text)

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
    return new_task


@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task_api(
        task_data: TaskCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == task_data.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    new_task = Task(
        **task_data.dict(),
        owner_id=current_user.id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@router.get("/", response_model=List[TaskOut])
def get_my_tasks_api(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    tasks = db.query(Task).filter(Task.owner_id == current_user.id).all()
    return tasks


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_api(
        task_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    task_query = db.query(Task).filter(Task.id == task_id)
    task = task_query.first()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this task")

    task_query.delete(synchronize_session=False)
    db.commit()
    return