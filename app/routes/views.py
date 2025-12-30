from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()

# Hier sagen wir Python, wo die HTML-Dateien liegen
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
async def home(request: Request):
    # Zeige die Startseite an und übergib die Anfrage (für User-Session etc.)
    return templates.TemplateResponse("index.html", {"request": request})

