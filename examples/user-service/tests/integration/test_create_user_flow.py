from uuid import UUID

from src.flows.user.create_user_flow import create_user_flow
from tests.integration.fakes import FakeDatabase, FakeLogger, FixedIdGenerator

USER_ID = UUID("12345678-1234-5678-1234-567812345678")
IDS = FixedIdGenerator(USER_ID)
ANA = {"email": "ana@gmail.com", "name": "Ana"}


def test_creates_user_with_injected_id_and_logs_it():
    db, logger = FakeDatabase(), FakeLogger()
    response = create_user_flow(db, IDS, logger, ANA)
    assert response.status == 201
    assert response.body == {"id": str(USER_ID), "email": "ana@gmail.com", "name": "Ana"}
    assert db.rows == [{"id": str(USER_ID), "email": "ana@gmail.com", "name": "Ana"}]
    assert logger.entries == [{"level": "info", "message": "create user", "context": {"status": 201, "error": None}}]


def test_blocks_disposable_email():
    db, logger = FakeDatabase(), FakeLogger()
    response = create_user_flow(db, IDS, logger, {"email": "ana@tempmail.com", "name": "Ana"})
    assert (response.status, response.body["error"]) == (422, "email_domain_not_allowed")
    assert db.rows == []
    assert logger.entries == [
        {"level": "error", "message": "create user", "context": {"status": 422, "error": "email_domain_not_allowed"}}
    ]


def test_rejects_duplicate_email():
    db, logger = FakeDatabase(), FakeLogger()
    create_user_flow(db, IDS, logger, ANA)
    response = create_user_flow(db, IDS, logger, ANA)
    assert (response.status, response.body["error"]) == (409, "user_already_exists")


def test_invalid_payload_is_answered_and_logged_by_the_flow():
    logger = FakeLogger()
    response = create_user_flow(FakeDatabase(), IDS, logger, {"email": "nope"})
    assert (response.status, response.body["error"]) == (422, "invalid_payload")
    assert logger.entries[0]["context"] == {"status": 422, "error": "invalid_payload"}


def test_storage_failure_is_a_domain_error():
    response = create_user_flow(FakeDatabase(fail=True), IDS, FakeLogger(), ANA)
    assert (response.status, response.body["error"]) == (500, "storage_failure")
