from pydantic import BaseModel

# Input: What the User sends ("Buy sugar")
class TaskGenerateRequest(BaseModel):
    text: str

# Output: What the api answers
class TaskGenerateResponse(BaseModel):
    summary: str
    description: str
    priority: str
    category: str
