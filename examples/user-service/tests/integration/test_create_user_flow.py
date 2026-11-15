from src.domains.user import CreateUserInput
from src.flows.user.create_user_flow import create_user_flow
from tests.integration.fake_database import FakeDatabaseClient


def test_creates_user():
    db = FakeDatabaseClient()
    output = create_user_flow(db, CreateUserInput(email="ana@gmail.com", name="Ana")).unwrap()
    assert output.email == "ana@gmail.com"
    assert len(db.rows) == 1


def test_blocks_disposable_email():
    db = FakeDatabaseClient()
    result = create_user_flow(db, CreateUserInput(email="ana@tempmail.com", name="Ana"))
    assert result.failure()
    assert db.rows == []


def test_rejects_duplicate_email():
    db = FakeDatabaseClient()
    create_user_flow(db, CreateUserInput(email="ana@gmail.com", name="Ana"))
    result = create_user_flow(db, CreateUserInput(email="ana@gmail.com", name="Ana 2"))
    assert result.failure() == "A user with this email already exists"
