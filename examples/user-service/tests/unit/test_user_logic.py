from src.domains.user import CreateUserOutcome, CreateUserOutput, UserError, UserRecord, UserRuleCheck
from src.logics.user_logic import (
    check_email_domain,
    check_user_is_new,
    resolve_create_user_log_level,
    resolve_create_user_status,
)


def test_accepts_allowed_domain():
    assert check_email_domain("ana@gmail.com") == UserRuleCheck()


def test_rejects_blocked_domain():
    assert check_email_domain("ana@tempmail.com") == UserRuleCheck(error=UserError.EMAIL_DOMAIN_NOT_ALLOWED)


def test_user_is_new_when_no_records():
    assert check_user_is_new([]) == UserRuleCheck()


def test_user_is_not_new_when_records_found():
    record = UserRecord(id="1", email="ana@gmail.com", name="Ana")
    assert check_user_is_new([record]) == UserRuleCheck(error=UserError.USER_ALREADY_EXISTS)


def test_status_is_201_on_success():
    output = CreateUserOutput(id="1", email="ana@gmail.com", name="Ana")
    assert resolve_create_user_status(CreateUserOutcome(output=output)) == 201


def test_status_maps_each_error():
    expected = {
        UserError.INVALID_PAYLOAD: 422,
        UserError.EMAIL_DOMAIN_NOT_ALLOWED: 422,
        UserError.USER_ALREADY_EXISTS: 409,
        UserError.STORAGE_FAILURE: 500,
    }
    for error, status in expected.items():
        assert resolve_create_user_status(CreateUserOutcome(error=error)) == status


def test_every_error_has_a_configured_status():
    for error in UserError:
        assert isinstance(resolve_create_user_status(CreateUserOutcome(error=error)), int)


def test_every_error_has_a_configured_message():
    from src.resources.user_rules import USER_ERROR_MESSAGES

    assert set(USER_ERROR_MESSAGES) == {error.value for error in UserError}


def test_log_level_is_info_on_success_and_error_on_failure():
    output = CreateUserOutput(id="1", email="ana@gmail.com", name="Ana")
    assert resolve_create_user_log_level(CreateUserOutcome(output=output)) == "info"
    assert resolve_create_user_log_level(CreateUserOutcome(error=UserError.STORAGE_FAILURE)) == "error"
