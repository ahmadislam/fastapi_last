from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
import os

from app import models, schemas, crud
from app.database import engine, SessionLocal
from app.routers import users, tasks
from app.auth import get_current_active_user

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

templates = Jinja2Templates(directory="app/templates")

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/protected")
async def protected_route(current_user: schemas.User = Depends(get_current_active_user)):
    return {"message": f"Welcome, {current_user.username}!"}

@app.post("/current-task")
async def create_current_task(
    task_name: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    current_time = datetime.now()
    task = schemas.TaskCreate(
        title=task_name,
        description=f"Created at {current_time.strftime('%Y-%m-%d %H:%M:%S')}",
        due_date=current_time.date()
    )
    return crud.create_user_task(db=db, task=task, user_id=current_user.id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)