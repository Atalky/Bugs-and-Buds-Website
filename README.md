# My Blog

FastAPI blog starter with server-rendered pages (Jinja2) and a SQLite database via SQLAlchemy.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

```powershell
uvicorn app.main:app --reload
```

Visit http://127.0.0.1:8000

## Structure

- `app/main.py` - routes
- `app/models.py` - SQLAlchemy models
- `app/schemas.py` - Pydantic schemas (used by the JSON API)
- `app/database.py` - DB engine/session setup
- `app/templates/` - Jinja2 HTML templates
- `app/static/` - CSS/JS/images
