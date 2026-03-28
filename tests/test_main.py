import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200


def test_create_project():
    r = client.post("/projects", json={"name": "my-project"})
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "my-project"
    assert "id" in data
    assert "created_at" in data


def test_create_project_with_description():
    r = client.post("/projects", json={"name": "my-project", "description": "A test project"})
    assert r.status_code == 201
    assert r.json()["description"] == "A test project"


def test_create_duplicate_project():
    client.post("/projects", json={"name": "my-project"})
    r = client.post("/projects", json={"name": "my-project"})
    assert r.status_code == 409


def test_create_invalid_name():
    r = client.post("/projects", json={"name": "invalid name!"})
    assert r.status_code == 400


def test_create_empty_name():
    r = client.post("/projects", json={"name": ""})
    assert r.status_code == 400


def test_create_name_too_long():
    r = client.post("/projects", json={"name": "a" * 65})
    assert r.status_code == 400


def test_list_projects():
    client.post("/projects", json={"name": "proj1"})
    client.post("/projects", json={"name": "proj2"})
    r = client.get("/projects")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_list_projects_pagination():
    for i in range(5):
        client.post("/projects", json={"name": f"proj{i}"})
    r = client.get("/projects?skip=2&limit=2")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_get_project():
    created = client.post("/projects", json={"name": "test-proj"}).json()
    r = client.get(f"/projects/{created['id']}")
    assert r.status_code == 200
    assert r.json()["name"] == "test-proj"


def test_get_nonexistent_project():
    r = client.get("/projects/99999")
    assert r.status_code == 404


def test_update_project():
    created = client.post("/projects", json={"name": "old-name"}).json()
    r = client.put(f"/projects/{created['id']}", json={"name": "new-name"})
    assert r.status_code == 200
    assert r.json()["name"] == "new-name"


def test_update_retains_id():
    created = client.post("/projects", json={"name": "original"}).json()
    updated = client.put(f"/projects/{created['id']}", json={"name": "renamed"}).json()
    assert updated["id"] == created["id"]


def test_update_invalid_name():
    created = client.post("/projects", json={"name": "valid-name"}).json()
    r = client.put(f"/projects/{created['id']}", json={"name": "bad name!"})
    assert r.status_code == 400


def test_update_nonexistent_project():
    r = client.put("/projects/99999", json={"name": "whatever"})
    assert r.status_code == 404


def test_delete_project():
    created = client.post("/projects", json={"name": "to-delete"}).json()
    r = client.delete(f"/projects/{created['id']}")
    assert r.status_code == 204


def test_delete_nonexistent_project():
    r = client.delete("/projects/99999")
    assert r.status_code == 404
