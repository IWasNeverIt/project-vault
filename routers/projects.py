from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from database import Project, get_db
from cpp_utils import lib

router = APIRouter(prefix="/projects")


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


@router.post("", response_model=ProjectResponse, status_code=201)
def create_project(body: ProjectCreate, db: Session = Depends(get_db)):
    if not lib.valid_name(body.name.encode()):
        raise HTTPException(status_code=400, detail="Invalid project name")

    if db.query(Project).filter(Project.name == body.name).first():
        raise HTTPException(status_code=409, detail="Project already exists")

    project = Project(name=body.name, description=body.description)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=list[ProjectResponse])
def list_projects(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return db.query(Project).offset(skip).limit(limit).all()


@router.get("/{pid}", response_model=ProjectResponse)
def get_project(pid: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == pid).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{pid}", response_model=ProjectResponse)
def update_project(pid: int, body: ProjectUpdate, db: Session = Depends(get_db)):
    if not lib.valid_name(body.name.encode()):
        raise HTTPException(status_code=400, detail="Invalid project name")

    project = db.query(Project).filter(Project.id == pid).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project.name = body.name
    project.description = body.description
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{pid}", status_code=204)
def delete_project(pid: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == pid).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()
