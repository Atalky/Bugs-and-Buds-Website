import uuid

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


def _unique_username():
    """Generates a fresh username per test so runs don't collide on uniqueness."""
    return f"testuser_{uuid.uuid4().hex[:8]}"


def test_register_page_loads():
    response = client.get("/register")
    assert response.status_code == 200


def test_register_success_redirects_home():
    username = _unique_username()
    response = client.post(
        "/register",
        data={
            "username": username,
            "password": "correct-password",
            "confirm_password": "correct-password",
            "biography": "Test bio",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_register_password_mismatch_shows_error():
    response = client.post(
        "/register",
        data={
            "username": _unique_username(),
            "password": "correct-password",
            "confirm_password": "different-password",
        },
    )
    assert response.status_code == 400
    assert "Passwords do not match" in response.text

def test_register_duplicate_username_shows_error():
    payload = {
        "username": _unique_username(),
        "password": "correct-password",
        "confirm_password": "correct-password",
    }
    first = client.post("/register", data=payload, follow_redirects=False)
    assert first.status_code == 303

    second = client.post("/register", data=payload, follow_redirects=False)
    assert second.status_code == 400
    assert "already taken" in second.text


def test_login_page_loads():
    response = client.get("/login")
    assert response.status_code == 200


def test_login_success_redirects_home():
    username = _unique_username()
    password = "correct-password"
    client.post(
        "/register",
        data={"username": username, "password": password, "confirm_password": password},
        follow_redirects=False,
    )

    response = client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_login_wrong_password_shows_error():
    username = _unique_username()
    password = "correct-password"
    client.post(
        "/register",
        data={"username": username, "password": password, "confirm_password": password},
        follow_redirects=False,
    )

    response = client.post(
        "/login",
        data={"username": username, "password": "wrong-password"},
    )
    assert response.status_code == 401
    assert "Invalid username or password" in response.text