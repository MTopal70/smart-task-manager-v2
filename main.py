from fastapi import FastAPI
from app.database import init_db
from app.routes import project_routes
from app.routes import user_routes
from app.routes import task_routes

app = FastAPI()
app.include_router(project_routes.router)
app.include_router(user_routes.router)
app.include_router(task_routes.router)

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def read_root():
    return {"message": "Smart Task Manager API is running"}

