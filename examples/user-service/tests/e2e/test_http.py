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
    assert duplicate.status_code == 400


def test_post_users_invalid_payload():
    assert client().post("/users", json={"email": "nope"}).status_code == 422
