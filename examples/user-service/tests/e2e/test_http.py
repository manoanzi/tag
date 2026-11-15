from fastapi.testclient import TestClient

from src.main import create_app
from src.resources.settings import Settings


def client() -> TestClient:
    return TestClient(create_app(Settings(database_path=":memory:")).app)


def test_post_users_creates_and_rejects_duplicate():
    http = client()
    created = http.post("/users", json={"email": "ana@gmail.com", "name": "Ana"})
    assert created.status_code == 201
    assert created.json()["email"] == "ana@gmail.com"

    duplicate = http.post("/users", json={"email": "ana@gmail.com", "name": "Ana"})
    assert duplicate.status_code == 409
    assert duplicate.json()["error"] == "user_already_exists"


def test_post_users_rejects_disposable_email():
    response = client().post("/users", json={"email": "ana@tempmail.com", "name": "Ana"})
    assert response.status_code == 422
    assert response.json()["error"] == "email_domain_not_allowed"


def test_post_users_invalid_payload():
    response = client().post("/users", json={"email": "nope"})
    assert response.status_code == 422
    assert response.json()["error"] == "invalid_payload"


def test_post_users_missing_name_is_invalid():
    response = client().post("/users", json={"email": "ana@gmail.com"})
    assert response.status_code == 422
    assert response.json()["error"] == "invalid_payload"
