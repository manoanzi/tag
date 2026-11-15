from uuid import UUID

from returns.result import Failure

from src.domains.user import CreateUserInput, CreateUserOutput, UserError
from src.flows.user.create_user_flow import create_user_flow
from tests.integration.fakes import FakeDatabase, FixedIdGenerator

USER_ID = UUID("12345678-1234-5678-1234-567812345678")
IDS = FixedIdGenerator(USER_ID)
ANA = CreateUserInput(email="ana@gmail.com", name="Ana")


def test_creates_user_with_injected_id():
    db = FakeDatabase()
    output = create_user_flow(db, IDS, ANA).unwrap()
    assert output == CreateUserOutput(id=str(USER_ID), email="ana@gmail.com", name="Ana")
    assert db.rows == [{"id": str(USER_ID), "email": "ana@gmail.com", "name": "Ana"}]


def test_blocks_disposable_email():
    db = FakeDatabase()
    result = create_user_flow(db, IDS, CreateUserInput(email="ana@tempmail.com", name="Ana"))
    assert result == Failure(UserError.EMAIL_DOMAIN_NOT_ALLOWED)
    assert db.rows == []


def test_rejects_duplicate_email():
    db = FakeDatabase()
    create_user_flow(db, IDS, ANA)
    assert create_user_flow(db, IDS, ANA) == Failure(UserError.USER_ALREADY_EXISTS)


def test_storage_failure_is_a_domain_error():
    assert create_user_flow(FakeDatabase(fail=True), IDS, ANA) == Failure(UserError.STORAGE_FAILURE)
