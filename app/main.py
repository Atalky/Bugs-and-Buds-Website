from fastapi import FastAPI, Request, status, HTTPException, Depends, Form
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from datetime import date
from schemas import BlogCreate, BlogResponse

from .database import Base, engine, get_db
from .models import Post, User
from .auth import hash_password, verify_password

from sqlalchemy.orm import Session

# Password hashing helpers are defined in app/auth.py.

BASE_DIR = Path(__file__).resolve().parent   # always point to /Website/app, wherever you run from
app = FastAPI()
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

'''
Cookies - middleware 
'''
from starlette.middleware.sessions import SessionMiddleware
import os

app.add_middleware(SessionMiddleware, secret_key=os.environ["SECRET_KEY"])
'''
database
'''
Base.metadata.create_all(bind=engine)

'''
Index
'''
@app.get("/", include_in_schema=False)
def home(request: Request):
    all_posts = get_blogs()
    recent_posts = list(reversed(all_posts[-3:]))
    latest_post = recent_posts[0] if recent_posts else None
    return templates.TemplateResponse(
        request, "index.html",
        {"recent_posts": recent_posts, "latest_post": latest_post},
    )


'''
Tech Projects
'''
@app.get("/projects", include_in_schema=False)
def tech_projects(request: Request):
    return templates.TemplateResponse(request, "techproject.html", {})

'''
GET /login - renders the login form.
'''
@app.get("/login", include_in_schema=False)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {})

'''
GET /register - renders the signup form.
'''
@app.get("/register", include_in_schema=False)
def register_page(request: Request):
    return templates.TemplateResponse(request, "register.html", {})

'''
profile pages
'''
@app.get("/profile", include_in_schema=False)
def my_profile(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    return RedirectResponse(url=f"/profile/{user.username}", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/profile/{username}", include_in_schema=False)
def profile_page(request: Request, username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user_posts = [blog for blog in get_blogs() if blog["author"] == user.username]
    return templates.TemplateResponse(
        request, "profile.html",
        {"profile_user": user, "posts": user_posts},
    )
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
Api for blogs
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

'''
POST /register - creates a new user account from the signup form.
Expects form fields: username, password, confirm_password, biography.
'''
@app.post("/register", include_in_schema=False)
def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    biography: str = Form(""),
    db: Session = Depends(get_db),
):
    if password != confirm_password:
        return templates.TemplateResponse(
            request, "register.html",
            {"error": "Passwords do not match"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    existing = db.query(User).filter(User.username == username).first()
    if existing:
        return templates.TemplateResponse(
            request, "register.html",
            {"error": "Username already taken"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    user = User(
        username=username,
        hashed_password=hash_password(password),
        biography=biography,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    request.session["user_id"] = user.id
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

'''
POST /login - authenticates a user against the users table and starts a session.
Expects form fields: username, password.
'''
@app.post("/login", include_in_schema=False)
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            request, "login.html",
            {"error": "Invalid username or password"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    request.session["user_id"] = user.id
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)





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
    {
    "id": 13,
    "author": "Atal",
    "title": "Real User Accounts: Register, Login, and Three Bugs I Didn't See Coming",
    "content": (
        "Got user accounts working end to end — register, login, and passwords that "
        "are actually hashed before they ever touch the database. Added a User model "
        "(username, hashed password, a biography field, an admin flag for later) and "
        "wired /register and /login up to the real Postgres database instead of just "
        "rendering static forms. Password hashing started on bcrypt, but it turns out "
        "bcrypt has a hard 72-byte limit on input length and just throws instead of "
        "silently truncating — hit that almost immediately while testing. Swapped to "
        "Argon2id instead (passlib + argon2-cffi), which is the more modern, memory-hard "
        "choice anyway and doesn't have that ceiling. "
        "Three bugs along the way were worth remembering: a naming collision where my "
        "own `app.auth` import got shadowed the moment `app = FastAPI()` ran further "
        "down the same file, since both were using the name `app`; a schema-drift issue "
        "where I'd added a new `biography` column to the model, but SQLAlchemy's "
        "create_all() only creates brand-new tables — it never alters one that's already "
        "there, so the old users table had to be dropped and rebuilt; and a properly "
        "sneaky one in my own test suite, where Jinja2 was HTML-escaping an apostrophe "
        "in an error message so the rendered page said \"don&#39;t\" instead of \"don't\" "
        "— the page was correct, but a plain string-match test against it wasn't. "
        "Added seven new pytest cases covering the register and login success and "
        "failure paths, so I'm not manually clicking through the forms every time I "
        "touch this code. Live on Render now and tested end to end."
    ),
    "date_posted": "2026-09-22",
},
    {
        "id": 14,
        "author": "Atal",
        "title": "New project: Injection Guard (and learning how LLMs get tested)",
        "content": (
            "Started a new project today, separate from this site for now. I picked a real job to aim at, "
            "a Junior ML Engineer role in AI safety and security, and planned a one-week project that covers "
            "what it asks for. The project is Injection Guard: it attacks a small LLM with prompt-injection "
            "attacks to see how often it leaks a secret 'canary' string hidden in its instructions, then tests "
            "whether a trained detector in front of it makes those attacks fail more often. The plan is to "
            "report every number with a confidence interval rather than a single score, and later ship the "
            "detector as an API on AWS. "
            "Day one was mostly setup and learning. Set up a new repo with uv, ruff (a fast linter and "
            "formatter), pytest and pre-commit. My first attempt lived inside iCloud Drive in a folder with "
            "spaces and an ampersand in the path, which broke a uv command and would have had iCloud trying "
            "to sync thousands of files from the virtual environment and git history, so I moved it to a "
            "plain local dev folder. Wrote a threat model based on the OWASP Top 10 for LLM applications "
            "(LLM01, prompt injection) and, more importantly, decided what's out of scope: indirect injection "
            "through documents, multimodal attacks, adversarial suffixes and multi-turn attacks. That last one "
            "means my results will be a lower bound on the real risk, and I'd rather say that up front. "
            "The plan was to attack the phi3:mini model on my Raspberry Pi, but the Pi isn't set up or on "
            "the same network as my laptop, so I installed Ollama locally and made the model address a "
            "setting instead of hard-coding it, so it can point at the Pi later. The first real test taught "
            "me the most: I asked phi3:mini for exactly five words, and it gave six, then added a paragraph "
            "claiming it had used exactly five. So the model can't be trusted to report on its own behaviour. "
            "An attack will count as successful only if a plain string check finds the canary in the reply, "
            "and every run will use temperature 0 and a fixed seed so results are reproducible. Each reply "
            "takes about 5 seconds once the model is warm, which puts a few hundred attacks at under an hour. "
            "Spent time understanding Ollama's API properly: the outer JSON reply is always the same shape, "
            "but you can force the model's actual answer into a JSON schema with the format field, which is "
            "how the judge will return a typed verdict. I also decided to keep the system prompt in my own "
            "code rather than baking it into a custom Ollama model, so what was tested stays visible in the "
            "repo. Other small lessons: switched from Python 3.14 to 3.12 because AWS Lambda images and some "
            "ML libraries lag behind the newest release (and uv refused to pin 3.12 until I'd loosened "
            "requires-python first, so order matters); and publishing a branch on GitHub only pushes what's "
            "been committed, which is why my latest changes seemed to have vanished when they were just "
            "uncommitted. I logged every decision and the reason for it in a decisions file in the repo. "
            "To build intuition I played Lakera's Gandalf prompt-injection game, where you try to trick a "
            "model into revealing a password. Level 1 has no defences at all, and simply asking works, which "
            "is exactly the 'detector off' baseline I'll be measuring. I also got stuck at around 65% on a "
            "scored challenge, which showed me how much wording and randomness affect whether an attack "
            "lands. I'm keeping notes on which prompts work and why, to use as seed attacks later in the week. "
            "Also downloaded the deepset/prompt-injections dataset (kept out of git) and started exploring it: "
            "class balance, prompt lengths, language, and whether any texts appear in both the training and "
            "test sets, since that would make the detector's scores look better than they really are. "
            "Next up is finishing that analysis and training the first detector."
        ),
        "date_posted": "2026-09-30",
    },
    {
        "id": 15,
        "author": "Atal",
        "title": "Foreign keys, real authors, and a plan for private posts",
        "content": (
            "Spent today on the data model behind the next big feature. Posts used to store their author "
            "as a plain string; now they point at a real user through an author_id foreign key, and can "
            "optionally belong to a project through project_id. Users own projects, projects hold posts, and "
            "SQLAlchemy relationships let me walk between them in templates, like post.author.username, "
            "instead of writing joins by hand. "
            "The thing that finally made relationships click: SQLAlchemy works out which side is the one and "
            "which is the many purely from which table holds the foreign key column. back_populates only "
            "pairs two attributes up; it says nothing about direction. "
            "Two mistakes in my own first draft were worth remembering. I named the foreign key column and "
            "the relationship both author, and since a class body runs top to bottom like normal Python, the "
            "second line silently replaced the first and the column vanished. I also briefly had a unique "
            "username column on posts, which would have stopped anyone from ever writing a second post. "
            "Added six tests for the profile pages, taking the suite to 16 passing, and fixed CI, which had "
            "no SECRET_KEY set, so the app could not even import there once login was added. "
            "Also planned what comes next: an Instagram-style home page with a public Discover feed and a "
            "Following tab, where each post can be public, followers-only or close-friends-only on the same "
            "account."
        ),
        "date_posted": "2026-10-01",
    },
]
