from fastapi import FastAPI, Request , status, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path


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
        "title": "First Post.",
        "content": "first post. ",
        "date_posted": "2022-01-01",
    },
    {
        "id": 2,
        "author": "Atal",
        "title": "Second Post.",
        "content": "second post. ",
        "date_posted": "2022-01-02",
    },

]

def get_blogs():
    return blogs

@app.get("/blog", include_in_schema=False)
def blog_list(request: Request):
    return templates.TemplateResponse(request, "blog.html", {"blogs": get_blogs()})

@app.get("/api/blog")
def api_get_blogs():
    return get_blogs()

def find_blog_or_404(blog_id: int) -> dict:
    for blog in blogs:
        if blog["id"] == blog_id:
            return blog
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")


@app.get("/blog/{blog_id}", include_in_schema=False, name="blog_detail")
def blog_detail(request: Request, blog_id: int):
    found = find_blog_or_404(blog_id)
    return templates.TemplateResponse(request, "blog_detail.html", {"blog": found})


@app.get("/api/blog/{blog_id}")
def get_blog_api(blog_id: int):
    return find_blog_or_404(blog_id)

'''
Calendar
'''
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
exception handler
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
