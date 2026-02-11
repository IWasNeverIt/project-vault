from database import SessionLocal, Project, init_db
from fastapi import FastAPI, HTTPException
import ctypes
import os

app = FastAPI()
init_db()

# Load C++ shared library
LIB_PATH = os.path.join(os.path.dirname(__file__), "libproject.so")
lib = ctypes.CDLL(LIB_PATH)

lib.valid_name.argtypes = [ctypes.c_char_p]
lib.valid_name.restype = ctypes.c_bool

lib.hash_name.argtypes = [ctypes.c_char_p]
lib.hash_name.restype = ctypes.c_uint

@app.get("/")
def root():
    return {"status": "ProjectVault API running"}

@app.post("/projects")
def create_project(name: str):
    if not lib.valid_name(name.encode()):
        raise HTTPException(status_code=400, detail="Invalid project name")

    pid = lib.hash_name(name.encode())

    db = SessionLocal()

    existing = db.query(Project).filter(Project.id == pid).first()
    if existing:
        db.close()
        raise HTTPException(status_code=409, detail="Project already exists")

    project = Project(id=pid, name=name)
    db.add(project)
    db.commit()
    db.close()

    return {"id": pid, "name": name}

@app.get("/projects")
def list_projects():
    db = SessionLocal()
    projects = db.query(Project).all()
    db.close()
    return [{"id": p.id, "name": p.name} for p in projects]

@app.get("/projects/{pid}")
def get_project(pid: int):
    db = SessionLocal()
    project = db.query(Project).filter(Project.id == pid).first()
    db.close()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return {"id": project.id, "name": project.name}

@app.put("/projects/{pid}")
def update_project(pid: int, name: str):
    if not lib.valid_name(name.encode()):
        raise HTTPException(status_code=400, detail="Invalid project name")

    db = SessionLocal()
    project = db.query(Project).filter(Project.id == pid).first()

    if not project:
        db.close()
        raise HTTPException(status_code=404, detail="Project not found")

    project.name = name
    db.commit()
    db.close()

    return {"id": pid, "name": name}
@app.delete("/projects/{pid}")
def delete_project(pid: int):
    db = SessionLocal()
    project = db.query(Project).filter(Project.id == pid).first()

    if not project:
        db.close()
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()
    db.close()

    return {"deleted": pid}
