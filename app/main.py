from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

blogs: list[dict] = [
    {
        "id": 1,
        "author": "Atal",
        "title": "This WORD of MINE and MIND.",
        "content": "Lost for words.",
        "date_posted": "2022-01-01",
    },
]


@app.get("/", include_in_schema=False)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/blog", include_in_schema=False)
def blog(request: Request):
    
    
    return templates.TemplateResponse(request, "blog.html", {"blogs": blogs})

@app.get("/api/blog")
def get_blogs():
    return blogs