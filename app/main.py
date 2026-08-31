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


def get_events():
    return [
        {"id": 1, "title": "Gym", "top": 480, "height": 60, "colour": "#0d6efd"},        # 08:00
        {"id": 2, "title": "Deep work", "top": 600, "height": 120, "colour": "#dc3545"}, # 10:00
    ]


@app.get("/", include_in_schema=False)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {"events": get_events()})


@app.get("/blog", include_in_schema=False)
def blog(request: Request):
    return templates.TemplateResponse(request, "blog.html", {"blogs": blogs})


@app.get("/api/blog")
def get_blogs():
    return blogs


@app.get("/api/calendar")
def api_calendar():
    return get_events()