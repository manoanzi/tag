from returns.result import Failure, Success

from src.domains.user import CreateUserOutput, UserError, UserRecord
from src.logics.user_logic import ensure_user_not_exists, resolve_create_user_status, validate_email_domain


def test_accepts_allowed_domain():
    assert validate_email_domain("ana@gmail.com") == Success("ana@gmail.com")


def test_rejects_blocked_domain():
    assert validate_email_domain("ana@tempmail.com") == Failure(UserError.EMAIL_DOMAIN_NOT_ALLOWED)


def test_user_does_not_exist_when_no_records():
    assert ensure_user_not_exists([]) == Success(None)


def test_user_exists_when_records_found():
    record = UserRecord(id="1", email="ana@gmail.com", name="Ana")
    assert ensure_user_not_exists([record]) == Failure(UserError.USER_ALREADY_EXISTS)


def test_status_is_201_on_success():
    output = CreateUserOutput(id="1", email="ana@gmail.com", name="Ana")
    assert resolve_create_user_status(Success(output)) == 201


def test_status_maps_each_error():
    assert resolve_create_user_status(Failure(UserError.INVALID_PAYLOAD)) == 422
    assert resolve_create_user_status(Failure(UserError.EMAIL_DOMAIN_NOT_ALLOWED)) == 422
    assert resolve_create_user_status(Failure(UserError.USER_ALREADY_EXISTS)) == 409
    assert resolve_create_user_status(Failure(UserError.STORAGE_FAILURE)) == 500
