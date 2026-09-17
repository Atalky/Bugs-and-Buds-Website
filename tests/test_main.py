from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_home_pade_loads():
    response = client.get("/")
    assert response.status_code == 200

def test_projects_page_loads():
    response = client.get("/projects")
    assert response.status_code == 200


def test_blog_api_returns_json_list():
    response = client.get("/api/blog")
    assert response.status_code == 200
    assert isinstance(response.json(), list)