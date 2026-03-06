from database import SessionLocal, Project, init_db
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import ctypes
import os

app = FastAPI()
init_db()

# Load C++ shared library
LIB_PATH = os.path.join(os.path.dirname(__file__), "libproject.so")
lib = ctypes.CDLL(LIB_PATH)

lib.valid_name.argtypes = [ctypes.c_char_p]
lib.valid_name.restype = ctypes.c_bool


# --- Request / Response Models ---

class ProjectCreate(BaseModel):
    name: str

class ProjectUpdate(BaseModel):
    name: str

class ProjectResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


# --- DB Dependency ---

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Routes ---

@app.get("/")
def root():
    return {"status": "ProjectVault API running"}


@app.post("/projects", response_model=ProjectResponse, status_code=201)
def create_project(body: ProjectCreate, db: Session = Depends(get_db)):
    if not lib.valid_name(body.name.encode()):
        raise HTTPException(status_code=400, detail="Invalid project name")

    if db.query(Project).filter(Project.name == body.name).first():
        raise HTTPException(status_code=409, detail="Project already exists")

    project = Project(name=body.name)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@app.get("/projects", response_model=list[ProjectResponse])
def list_projects(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return db.query(Project).offset(skip).limit(limit).all()


@app.get("/projects/{pid}", response_model=ProjectResponse)
def get_project(pid: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == pid).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.put("/projects/{pid}", response_model=ProjectResponse)
def update_project(pid: int, body: ProjectUpdate, db: Session = Depends(get_db)):
    if not lib.valid_name(body.name.encode()):
        raise HTTPException(status_code=400, detail="Invalid project name")

    project = db.query(Project).filter(Project.id == pid).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project.name = body.name
    db.commit()
    db.refresh(project)
    return project


@app.delete("/projects/{pid}")
def delete_project(pid: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == pid).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()
    return {"deleted": pid}
