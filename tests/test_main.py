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

'''

'''

def _register(test_client, username, password="correct-password", biography=""):
    """Registers a user through the real /register route; leaves test_client logged in as them."""
    return test_client.post(
        "/register",
        data={
            "username": username,
            "password": password,
            "confirm_password": password,
            "biography": biography,
        },
        follow_redirects=False,
    )


def test_navbar_has_profile_link():
    response = client.get("/")
    assert 'href="/profile"' in response.text


def test_profile_redirects_to_login_when_logged_out():
    fresh_client = TestClient(app)  # no session cookie
    response = fresh_client.get("/profile", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_profile_redirects_to_own_page_when_logged_in():
    fresh_client = TestClient(app)
    username = _unique_username()
    _register(fresh_client, username)

    response = fresh_client.get("/profile", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == f"/profile/{username}"


def test_profile_page_shows_username_and_bio():
    username = _unique_username()
    _register(TestClient(app), username, biography="Test bio for the profile page")

    response = client.get(f"/profile/{username}")
    assert response.status_code == 200
    assert username in response.text
    assert "Test bio for the profile page" in response.text


def test_profile_page_without_bio_shows_placeholder():
    username = _unique_username()
    _register(TestClient(app), username)

    response = client.get(f"/profile/{username}")
    assert response.status_code == 200
    assert "No bio yet." in response.text


def test_profile_unknown_user_returns_404():
    response = client.get(f"/profile/{_unique_username()}")
    assert response.status_code == 404


def _new_user():
    """Registers a fresh user; returns (logged-in client, username)."""
    user_client = TestClient(app)
    username = _unique_username()
    _register(user_client, username)
    return user_client, username


def test_follow_increases_follower_count():
    _, target_name = _new_user()
    follower, _ = _new_user()

    response = follower.post(f"/profile/{target_name}/follow", follow_redirects=False)
    assert response.status_code == 303

    page = follower.get(f"/profile/{target_name}").text
    assert "1 followers" in page
    assert "Following" in page