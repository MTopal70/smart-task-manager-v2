from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.models.project import Project
from app.models.user import User
from app.schemas.project import  ProjectCreate, ProjectOut
from app.database import get_db
from app.oauth2 import get_current_user
router = APIRouter(prefix="/projects", tags=["projects"])

# CREATE

@router.post("/", response_model=ProjectOut)
def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    new_project = Project(**data.dict(), owner_id=current_user.id)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

# READ ALL

@router.get("/", response_model=list[ProjectOut])
def get_projects(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # Filter Projekte, wo owner_id == meine ID ist
    projects = db.query(Project).filter(Project.owner_id == current_user.id).all()
    return projects

# READ ONE

@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
        project_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    return project

# UPDATE

@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
        project_id: int,
        data: ProjectCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)  # <--- Türsteher
):
    project_query = db.query(Project).filter(Project.id == project_id)
    project = project_query.first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # SICHERHEITS-CHECK
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    # Update durchführen
    project_query.update(data.dict(), synchronize_session=False)
    db.commit()

    return project

# DELETE

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
        project_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)  # <--- Türsteher
):
    project_query = db.query(Project).filter(Project.id == project_id)
    project = project_query.first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # SICHERHEITS-CHECK
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    project_query.delete(synchronize_session=False)
    db.commit()
    return

