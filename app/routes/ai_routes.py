from fastapi import APIRouter
from app.services.ai_services import analyze_task_with_ai
from schemas import TaskGenerateRequest, TaskGenerateResponse

router = APIRouter(
    prefix="/ai",
    tags=["Artificial Intelligence"]
)

@router.post("/generate", response_model=TaskGenerateResponse)
def generate_task_suggestion(request: TaskGenerateRequest):
    """
    Nimmt einen Text, sendet ihn an Gemini und liefert einen strukturierten Task-Vorschlag.
    """
    # Hier rufen wir deinen Service auf
    ai_result = analyze_task_with_ai(request.text)
    return ai_result
