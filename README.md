# ProjectVault

A cross-language CRUD backend built with FastAPI, SQLite, and a native C++ shared library integrated via FFI.

## Tech Stack
- Python (FastAPI)
- SQLite (SQLAlchemy ORM)
- C++ (shared library, ctypes integration)
- Ubuntu (WSL)

## Features
- Full RESTful CRUD API
- Name validation via C++ shared library
- Persistent storage using SQLite
- Interactive API docs via Swagger

## Run Locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
g++ -shared -fPIC cpp/project_utils.cpp -o libproject.so
uvicorn main:app --reload
```

## Run Tests

```bash
source venv/bin/activate
pytest tests/ -v
```
