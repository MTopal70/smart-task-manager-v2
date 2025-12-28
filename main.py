from fastapi import FastAPI
from app.database import init_db
from contextlib import asynccontextmanager # <--- NEU
from app.routes import project_routes
from app.routes import user_routes
from app.routes import task_routes
from app.routes import ai_routes
from app.routes import auth

# 1. Der neue "Lifespan" Manager (ersetzt startup event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Was hier steht, passiert VOR dem Start
    init_db()
    yield
    # Was hier stünde, passiert NACH dem Stoppen (brauchen wir gerade nicht)

# 2. Wir übergeben lifespan an die App
app = FastAPI(lifespan=lifespan)

# 3. Router einbinden
app.include_router(user_routes.router)
app.include_router(project_routes.router)
app.include_router(task_routes.router)
app.include_router(ai_routes.router)
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "Smart Task Manager V2 API is running with AI 🧠"}

if __name__ == "__main__":
    import uvicorn
    # Startet den Server direkt aus dem Code heraus
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)