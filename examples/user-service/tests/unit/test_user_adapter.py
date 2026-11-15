from uuid import UUID

from returns.result import Failure, Success

from src.adapters.user_adapter import (
    to_create_user_input,
    to_create_user_output,
    to_create_user_response_body,
    to_query_params,
    to_storage_error,
    to_user_domain,
    to_user_from_rows,
    to_user_record,
)
from src.domains.user import CreateUserInput, User, UserError

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


def test_response_body_on_success_and_failure():
    output = to_create_user_output(USER)
    assert to_create_user_response_body(Success(output)) == output.model_dump()
    assert to_create_user_response_body(Failure(UserError.USER_ALREADY_EXISTS)) == {
        "error": "user_already_exists",
        "message": "A user with this email already exists",
    }
