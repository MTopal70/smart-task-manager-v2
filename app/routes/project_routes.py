from datetime import datetime
from fastapi import APIRouter, Depends, Form, Request, HTTPException
from starlette.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.services.ai_services import analyze_task_with_ai

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.post("/projects/create_web")
async def create_project_web(
        request: Request,
        title: str = Form(...),
        start_date: str = Form(...),  # Kommt als String vom HTML-Kalenderpicker
        ai_instructions: str = Form(None),  # Optional! Wenn leer -> Manuelles Projekt
        db: Session = Depends(get_db)
):
    # 1. User checken
    user_info = request.session.get('user')
    if not user_info:
        return RedirectResponse(url="/login", status_code=303)

    user_email = user_info.get('email')
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    # 2. Datum konvertieren (HTML sendet YYYY-MM-DD)
    try:
        dt_start = datetime.strptime(start_date, "%Y-%m-%d")
    except ValueError:
        dt_start = datetime.now()

    # 3. Das Projekt anlegen (Das passiert IMMER)
    new_project = Project(
        title=title,
        description=ai_instructions if not ai_instructions else "KI-generiertes Projekt",
        start_date=dt_start,
        owner_id=user.id
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)  # Damit wir die ID bekommen (new_project.id)

    # 4. Hybrid-Weiche: KI oder Manuell?
    if ai_instructions and len(ai_instructions.strip()) > 0:
        print(f"🤖 KI wird aktiviert für Projekt: {title}")
        try:
            # KI generiert Tasks
            ai_tasks = analyze_task_with_ai (ai_instructions)

            # Tasks in DB speichern und mit Projekt verknüpfen
            for t_data in ai_tasks:
                task = Task(
                    title=t_data.get('title'),
                    description=t_data.get('estimated_time'),
                    owner_id=user.id,
                    project_id=new_project.id,  # <--- Hier verknüpfen wir es!
                    created_at=dt_start  # Tasks starten am Projekttag
                )
                db.add(task)
            db.commit()
        except Exception as e:
            print(f"❌ KI Fehler: {e}")
    else:
        print(f"👤 Manuelles Projekt angelegt: {title}")

    # Zurück zum Kalender
    return RedirectResponse(url="/", status_code=303)

@router.get("/projects/{project_id}/board")
async def get_project_board(request: Request, project_id: int, db: Session = Depends(get_db)):
    user_info = request.session.get('user')
    if not user_info: return RedirectResponse(url="/login", status_code=303)

    # Projekt laden
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return RedirectResponse(url="/", status_code=303)

    # Tasks nach Status sortieren
    tasks_todo = [t for t in project.tasks if t.status == "todo"]
    tasks_progress = [t for t in project.tasks if t.status == "in_progress"]
    tasks_done = [t for t in project.tasks if t.status == "done"]

    return templates.TemplateResponse("kanban.html", {
        "request": request,
        "project": project,
        "todo": tasks_todo,
        "progress": tasks_progress,
        "done": tasks_done
    })


# --- NEU: Task verschieben (API für Drag & Drop) ---
@router.post("/tasks/{task_id}/move")
async def move_task(task_id: int, status: str = Form(...), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Status aktualisieren
    task.status = status
    db.commit()

    return JSONResponse(content={"success": True, "new_status": status})


# --- NEU: Einzelnen Task zum Projekt hinzufügen ---
@router.post("/projects/{project_id}/tasks/create")
async def create_task_in_project(
        project_id: int,
        title: str = Form(...),
        description: str = Form(None),
        request: Request = None,
        db: Session = Depends(get_db)
):
    user_info = request.session.get('user')
    if not user_info: return RedirectResponse(url="/login", status_code=303)

    # User ID finden
    user = db.query(User).filter(User.email == user_info.get('email')).first()

    # Task erstellen
    new_task = Task(
        title=title,
        description=description,
        status="todo",  # Kommt immer erst ins Backlog
        project_id=project_id,
        owner_id=user.id
    )
    db.add(new_task)
    db.commit()

    # Zurück zum Board
    return RedirectResponse(url=f"/projects/{project_id}/board", status_code=303)

