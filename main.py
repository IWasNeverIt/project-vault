from fastapi import FastAPI
from database import init_db
from routers.projects import router as projects_router

app = FastAPI()
init_db()

app.include_router(projects_router)


@app.get("/")
def root():
    return {"status": "ProjectVault API running"}
