from fastapi import FastAPI, Request , status, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from datetime import date
from schemas import BlogCreate, BlogResponse

from .database import Base, engine
from .models import Post

BASE_DIR = Path(__file__).resolve().parent   # always point to /Website/app, wherever you run from
app = FastAPI()
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

'''
database
'''
Base.metadata.create_all(bind=engine)

'''
Index
'''
@app.get("/", include_in_schema=False)
def home(request: Request):
    
    return templates.TemplateResponse(request, "index.html", {"events": get_events()})

'''
Blog
'''
blogs : list[dict] = [
    {
        "id": 1,
        "author": "Atal",
        "title": "My reason and goal for this devlog",
        "content": (
            "I set this project up to learn more about FastAPI and how to integrate AI into real services, "
            "including tool-using agents. My aim for this project and this devlog is to document my learning "
            "and how my understanding evolves as I go. I already have university-level Spring Boot experience "
            "(see my GitHub), and I'm now learning the Python equivalent for speed and for AI/ML integration. "
            "Today I went back through the FastAPI documentation to make sure the fundamentals were solid "
            "before building further on top of them."
        ),
        "date_posted": "2026-08-01",
    },
    {
        "id": 2,
        "author": "Atal",
        "title": "Initial commit",
        "content": "First commit on the project — scaffolding the FastAPI app that this devlog now runs on.",
        "date_posted": "2026-08-01",
    },
    {
        "id": 3,
        "author": "Atal",
        "title": "Clean up repo, add requirements",
        "content": "Went back through the early scaffolding and tidied it up, and added a requirements file so the project's dependencies are actually pinned down instead of just installed loose in whatever environment I happened to be using.",
        "date_posted": "2026-08-31",
    },
    {
        "id": 4,
        "author": "Atal",
        "title": "Blog list/detail routes, migrated to uv, started SQLAlchemy models",
        "content": "Added the blog list and blog-detail routes, sharing one 404 helper between them instead of repeating the lookup logic. Also switched the project over from pip to uv for dependency management, and started the SQLAlchemy models that will eventually replace the in-memory blogs list with a real database.",
        "date_posted": "2026-09-01",
    },
    {
        "id": 5,
        "author": "Atal",
        "title": "Custom error page, proper exception handlers",
        "content": "Added a custom error page and wired up handlers for both HTTP exceptions and validation errors, so a bad request returns something readable instead of FastAPI's default JSON dump. Also fixed a missing Path import that had been quietly relying on it being imported somewhere else.",
        "date_posted": "2026-09-02",
    },
    {
        "id": 6,
        "author": "Atal",
        "title": "Fixed the boot bugs and wrote the create-blog endpoint",
        "content": "Found and fixed three bugs that were stopping the app from starting at all: a schema class name that didn't match its import, a duplicate field on BlogBase that was silently overwriting itself, and a POST decorator with no function underneath it. Wrote the actual create_blog handler that decorator was missing, and gave BlogCreate real fields instead of the empty stub it had before.",
        "date_posted": "2026-09-07",
    },
    {        
    "id": 7,
        "author": "Atal",
        "title": "Dockerized it and got it live on Render",
        "content": (
            "Wrapped the app in a Dockerfile (python:3.13-slim base, uv sync for deps) so the build is "
            "reproducible instead of 'works on my machine.' First Render deploy attempt failed because "
            "the Dockerfile existed locally but had never actually been committed and pushed. Fixed that, "
            "and the devlog is now live at a real URL instead of just localhost. Also pulled the calendar "
            "off the public homepage for now — it was a rough single-day sketch, not the level of polish "
            "I actually want, and I'd rather get the framework, auth, and the AI feature solid first and "
            "come back to the calendar properly later. Replaced it with a simple intro page instead. Last "
            "thing: found a real mobile bug where the devlog post cards used a rounded-pill shape that broke "
            "on longer post text, overflowing off the card on phone screens — swapped it for a normal "
            "rounded corner."
        ),
        "date_posted": "2026-09-08",
    },
    {
        "id": 8,
        "author": "Atal",
        "title": "Tech projects page and a proper design pass",
        "content": (
            "Added a proper Tech Projects page with its own nav link, then spent the rest of the day "
            "on layout cleanup — stripped out leftover unused styles and stray graphs/images that had "
            "been cluttering things, fixed another layout bug on the devlog view, and went through the "
            "design one more time to actually get it looking right instead of just 'working.' Filled in "
            "real content for the Tech Projects page, added an underline to the active nav link, and "
            "centered the page titles so they're consistent across pages. Also caught a small but "
            "annoying navbar bug — one of the links had the wrong id, so it wasn't highlighting correctly."
        ),
        "date_posted": "2026-09-09",
    },
    {
        "id": 9,
        "author": "Atal",
        "title": "Added smoke tests ahead of CI/CD",
        "content": "Added the first proper smoke tests — home page, /projects, and /api/blog — so there's an automated baseline check that the app actually boots and the main routes respond, ahead of plugging this into a CI pipeline.",
        "date_posted": "2026-09-10",
    },
    {
        "id": 10,
        "author": "Atal",
        "title": "Got CI/CD Actually Running on GitHub Actions",
        "content": (
            "Got the smoke tests from a few days ago actually running automatically — added a GitHub "
            "Actions workflow that runs pytest on every push instead of only on my machine. Hit a "
            "genuinely silly bug along the way: I'd accidentally committed a duplicate, broken copy of "
            "my test file into the wrong folder, which had a broken import and risked clashing with the "
            "real test file by name. Deleted the wrong one first, then the right one, before sorting out "
            "which file actually belonged where and fixing the import. CI is green now."
        ),
        "date_posted": "2026-09-17",
    },
    {
        "id": 11,
        "author": "Atal",
        "title": "Wiring Up a Real Database (and Everything That Went Wrong Along the Way)",
        "content": (
            "Finally replaced the SQLite stub with a real PostgreSQL database, running in Docker "
            "instead of installed natively after the native Windows installer kept getting stuck in "
            "a broken delete-and-reinstall loop. Moved the connection string into a .env file (kept "
            "out of git) and switched database.py to build off that instead of a hardcoded SQLite "
            "path. Took three stacked bugs before it actually worked: a Docker volume that silently "
            "ignored a new password because Postgres only applies it on first initialization, a "
            "leftover native Postgres install from that earlier failed attempt quietly squatting on "
            "the default port and swallowing my connections with no obvious sign it was even involved, "
            "and a table that refused to appear because I'd never actually imported my model class "
            "anywhere, so SQLAlchemy had nothing registered to create. All three produced nearly "
            "identical error messages, which was the real lesson — 'wrong password' and 'you're not "
            "even talking to the database you think you are' can look exactly the same from the "
            "outside. The database is live now, but the app is still reading from the same in-memory "
            "list as before — wiring the actual routes up to it is next, along with real user accounts "
            "so posting isn't wide open to anyone who finds the API endpoint."
        ),
        "date_posted": "2026-09-17",
    },
        {
        "id": 12,
        "author": "Atal",
        "title": "CI Needs Its Own Database Too",
        "content": (
            "Pushing the real database change immediately broke CI — GitHub Actions had no "
            "DATABASE_URL at all, since my .env file only exists locally and is (correctly) "
            "gitignored, so create_engine() was getting None and crashing before a single test "
            "could even run. Fixed it by giving the CI job its own throwaway Postgres database: a "
            "service container that spins up alongside the test run, with a health check so tests "
            "don't start before it's actually ready to accept connections, and a DATABASE_URL "
            "pointing at that temporary database instead of anything real. Good reminder that "
            "local secrets don't travel with you to CI — every environment needs to be told where "
            "its own database actually lives."
        ),
        "date_posted": "2026-09-17",
    },
]

'''
Tech Projects
'''
@app.get("/projects", include_in_schema=False)
def tech_projects(request: Request):
    return templates.TemplateResponse(request, "techproject.html", {})

'''
blogs
'''
def get_blogs():
    return blogs

@app.get("/blog", include_in_schema=False)
def blog_list(request: Request):
    return templates.TemplateResponse(request, "blog.html", {"blogs": get_blogs()})

@app.get("/blog/{blog_id}", include_in_schema=False, name="blog_detail")
def blog_detail(request: Request, blog_id: int):
    found = find_blog_or_404(blog_id)
    return templates.TemplateResponse(request, "blog_detail.html", {"blog": found})


'''
Api
'''

@app.get("/api/blog", response_model=list[BlogResponse])
def api_get_blogs():
    return get_blogs()



def find_blog_or_404(blog_id: int) -> dict:
    for blog in blogs:
        if blog["id"] == blog_id:
            return blog
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")


@app.get("/api/blog/{blog_id}", response_model=BlogResponse)
def get_blog_api(blog_id: int):
    return find_blog_or_404(blog_id)

'''
Create Blog
'''

@app.post("/api/blog", response_model=BlogResponse, status_code=status.HTTP_201_CREATED)
def create_blog(payload: BlogCreate):
    new_id = max((blog["id"] for blog in blogs), default=0) + 1
    new_blog = {
        "id": new_id,
        "author": "Atal",
        "title": payload.title,
        "content": payload.content,
        "date_posted": date.today().isoformat(),
    }
    blogs.append(new_blog)
    return new_blog


def get_events():
    return [
        {"id": 1, "title": "Gym", "top": 480, "height": 60, "colour": "#0d6efd"},        # 08:00
        {"id": 2, "title": "Deep work", "top": 600, "height": 120, "colour": "#dc3545"}, # 10:00
    ]


@app.get("/api/calendar")
def api_calendar():
    return get_events()


'''
exception handler
'''
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exception: StarletteHTTPException):
    if request.url.path.startswith("/api"):
        return JSONResponse(status_code=exception.status_code, 
                            content={"detail": exception.detail})
    
    return templates.TemplateResponse(
        request, "error.html",
        {
        "status_code": exception.status_code, 
        "message": exception.detail
        },
        status_code=exception.status_code,
    )

'''
exception handler validaiton 
'''
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, 
                            content={"detail": exception.errors()})
    
    return templates.TemplateResponse(
        request, "error.html",
        {
        "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT, 
        "message": "Invalid request"
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )
