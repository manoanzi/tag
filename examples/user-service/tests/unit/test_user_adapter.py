from uuid import UUID

from returns.result import Failure, Success

from src.adapters.user_adapter import (
    to_create_user_input,
    to_create_user_log_entry,
    to_create_user_outcome,
    to_create_user_output,
    to_create_user_response,
    to_rule_result,
    to_single_user_record,
    to_storage_error,
    to_user_domain,
    to_user_from_record,
    to_user_query_params,
    to_user_record,
    to_user_records,
)
from src.domains.user import CreateUserInput, CreateUserOutcome, CreateUserResponse, User, UserError, UserRuleCheck

USER_ID = UUID("12345678-1234-5678-1234-567812345678")
USER = User(id=USER_ID, email="ana@gmail.com", name="Ana")
ROW = {"id": str(USER_ID), "email": "ana@gmail.com", "name": "Ana"}


def test_tolerant_reader_ignores_unknown_fields():
    result = to_create_user_input({"email": "ana@gmail.com", "name": "Ana", "nickname": "ignored"})
    assert result == Success(CreateUserInput(email="ana@gmail.com", name="Ana"))


def test_missing_or_empty_fields_are_invalid_not_defaulted():
    assert to_create_user_input({"email": "ana@gmail.com"}) == Failure(UserError.INVALID_PAYLOAD)
    assert to_create_user_input({"email": "ana@gmail.com", "name": ""}) == Failure(UserError.INVALID_PAYLOAD)
    assert to_create_user_input({"email": "not-an-email", "name": "Ana"}) == Failure(UserError.INVALID_PAYLOAD)


def test_rule_check_becomes_pipeline_step():
    assert to_rule_result(UserRuleCheck()) == Success(None)
    assert to_rule_result(UserRuleCheck(error=UserError.USER_ALREADY_EXISTS)) == Failure(UserError.USER_ALREADY_EXISTS)


def test_to_user_domain_is_pure():
    data = CreateUserInput(email="ana@gmail.com", name="Ana")
    assert to_user_domain(data, USER_ID) == to_user_domain(data, USER_ID) == USER


def test_domain_to_record_to_query_params():
    assert to_user_query_params(to_user_record(USER)) == ROW


def test_rows_to_records_to_domain():
    records = to_user_records([ROW])
    assert to_single_user_record(records).map(to_user_from_record) == Success(USER)


def test_write_without_returned_row_is_a_storage_failure():
    assert to_single_user_record([]) == Failure(UserError.STORAGE_FAILURE)


def test_storage_exception_becomes_domain_error():
    assert to_storage_error(RuntimeError("disk full")) == UserError.STORAGE_FAILURE


def test_result_becomes_outcome_schema():
    output = to_create_user_output(USER)
    assert to_create_user_outcome(Success(output)) == CreateUserOutcome(output=output)
    assert to_create_user_outcome(Failure(UserError.STORAGE_FAILURE)) == CreateUserOutcome(error=UserError.STORAGE_FAILURE)


def test_response_from_outcome():
    output = to_create_user_output(USER)
    assert to_create_user_response(201, CreateUserOutcome(output=output)) == CreateUserResponse(
        status=201, body=output.model_dump()
    )
    assert to_create_user_response(409, CreateUserOutcome(error=UserError.USER_ALREADY_EXISTS)) == CreateUserResponse(
        status=409, body={"error": "user_already_exists", "message": "A user with this email already exists"}
    )


def test_log_entry_from_outcome():
    output = to_create_user_output(USER)
    assert to_create_user_log_entry(CreateUserOutcome(output=output)) == {
        "level": "info",
        "message": "user created",
        "context": {"user_id": str(USER_ID)},
    }
    assert to_create_user_log_entry(CreateUserOutcome(error=UserError.INVALID_PAYLOAD)) == {
        "level": "error",
        "message": "could not create user",
        "context": {"error": "invalid_payload"},
    }
