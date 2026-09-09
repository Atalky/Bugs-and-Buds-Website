from fastapi import FastAPI, Request , status, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from datetime import date
from schemas import BlogCreate, BlogResponse

BASE_DIR = Path(__file__).resolve().parent   # always point to /Website/app, wherever you run from
app = FastAPI()
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


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
