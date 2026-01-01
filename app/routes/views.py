import calendar
from datetime import datetime
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.project import Project  # <--- WICHTIG: Projekt importieren
from app.models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

DEUTSCHE_MONATE = {
    1: "Januar", 2: "Februar", 3: "März", 4: "April", 5: "Mai", 6: "Juni",
    7: "Juli", 8: "August", 9: "September", 10: "Oktober", 11: "November", 12: "Dezember"
}


@router.get("/")
async def home(request: Request, year: int = None, month: int = None, db: Session = Depends(get_db)):
    user_info = request.session.get('user')
    projects_by_date = {}  # <--- Wir sammeln jetzt Projekte

    # Datum berechnen
    now = datetime.now()
    if year is None: year = now.year
    if month is None: month = now.month

    if month < 1: month = 1
    if month > 12: month = 12

    # Navigation berechnen
    prev_month = 12 if month == 1 else month - 1
    prev_year = year - 1 if month == 1 else year
    next_month = 1 if month == 12 else month + 1
    next_year = year + 1 if month == 12 else year

    month_name = f"{DEUTSCHE_MONATE[month]} {year}"
    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdayscalendar(year, month)

    # Daten laden
    if user_info:
        user_email = user_info.get('email')
        db_user = db.query(User).filter(User.email == user_email).first()

        if db_user:
            # Wir holen alle PROJEKTE des Users
            all_projects = db.query(Project).filter(Project.owner_id == db_user.id).all()

            for p in all_projects:
                # Wir nutzen das Startdatum des Projekts
                p_date = p.start_date
                if p_date.month == month and p_date.year == year:
                    day = p_date.day
                    if day not in projects_by_date:
                        projects_by_date[day] = []
                    projects_by_date[day].append(p)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "month_name": month_name,
        "month_days": month_days,
        "projects_by_date": projects_by_date,  # <--- Neue Variable
        "current_day": now.day,
        "current_month": now.month,
        "view_month": month,
        "view_year": year,
        "prev_year": prev_year, "prev_month": prev_month,
        "next_year": next_year, "next_month": next_month
    })