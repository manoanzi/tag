from uuid import UUID

from returns.result import Failure, Success

from src.adapters.user_adapter import (
    to_create_user_input,
    to_create_user_output,
    to_create_user_log_entry,
    to_create_user_outcome,
    to_create_user_response,
    to_query_params,
    to_rule_result,
    to_storage_error,
    to_user_domain,
    to_user_from_rows,
    to_user_record,
)
from src.domains.user import CreateUserInput, CreateUserOutcome, CreateUserResponse, User, UserError, UserRuleCheck

USER_ID = UUID("12345678-1234-5678-1234-567812345678")
USER = User(id=USER_ID, email="ana@gmail.com", name="Ana")


def test_tolerant_reader_ignores_unknown_fields():
    result = to_create_user_input({"email": "ana@gmail.com", "name": "Ana", "nickname": "ignored"})
    assert result == Success(CreateUserInput(email="ana@gmail.com", name="Ana"))


def test_invalid_payload_becomes_domain_error():
    assert to_create_user_input({"email": "not-an-email"}) == Failure(UserError.INVALID_PAYLOAD)


def test_to_user_domain_is_pure():
    data = CreateUserInput(email="ana@gmail.com", name="Ana")
    assert to_user_domain(data, USER_ID) == to_user_domain(data, USER_ID) == USER


def test_record_and_query_params_use_primitive_types():
    record = to_user_record(USER)
    assert to_query_params(record) == {"id": str(USER_ID), "email": "ana@gmail.com", "name": "Ana"}


def test_rows_back_to_domain():
    assert to_user_from_rows([{"id": str(USER_ID), "email": "ana@gmail.com", "name": "Ana"}]) == USER


def test_storage_exception_becomes_domain_error():
    assert to_storage_error(RuntimeError("disk full")) == UserError.STORAGE_FAILURE


def test_response_on_success_and_failure():
    output = to_create_user_output(USER)
    assert to_create_user_response(201, Success(output)) == CreateUserResponse(status=201, body=output.model_dump())
    assert to_create_user_response(409, Failure(UserError.USER_ALREADY_EXISTS)) == CreateUserResponse(
        status=409,
        body={"error": "user_already_exists", "message": "A user with this email already exists"},
    )


def test_log_entry_on_success_and_failure():
    output = to_create_user_output(USER)
    assert to_create_user_log_entry(Success(output)) == {
        "level": "info",
        "message": "user created",
        "context": {"user_id": str(USER_ID)},
    }
    assert to_create_user_log_entry(Failure(UserError.INVALID_PAYLOAD)) == {
        "level": "error",
        "message": "could not create user",
        "context": {"error": "invalid_payload"},
    }


def test_rule_check_becomes_pipeline_step():
    assert to_rule_result(UserRuleCheck()) == Success(None)
    assert to_rule_result(UserRuleCheck(error=UserError.USER_ALREADY_EXISTS)) == Failure(UserError.USER_ALREADY_EXISTS)


def test_result_becomes_outcome_schema():
    output = to_create_user_output(USER)
    assert to_create_user_outcome(Success(output)) == CreateUserOutcome(output=output)
    assert to_create_user_outcome(Failure(UserError.STORAGE_FAILURE)) == CreateUserOutcome(error=UserError.STORAGE_FAILURE)
