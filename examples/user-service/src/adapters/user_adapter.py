from typing import Any
from uuid import UUID

from returns.maybe import Maybe
from returns.result import Failure, Result, Success, safe

from src.domains.user import (
    CreateUserInput,
    CreateUserOutcome,
    CreateUserOutput,
    CreateUserResponse,
    User,
    UserError,
    UserRecord,
    UserRuleCheck,
)
from src.protocols.logger import LogEntry
from src.resources.user_rules import USER_ERROR_MESSAGES


def to_create_user_input(raw: dict[str, Any]) -> Result[CreateUserInput, UserError]:
    # Tolerant Reader: unknown fields are ignored, missing ones are invalid (never defaulted).
    return safe(CreateUserInput.model_validate)(raw).alt(lambda _: UserError.INVALID_PAYLOAD)


def to_rule_result(check: UserRuleCheck) -> Result[None, UserError]:
    """Turns a Logic decision (schema) into a step of the Result pipeline."""
    return Maybe.from_optional(check.error).map(Failure).value_or(Success(None))


def to_user_domain(data: CreateUserInput, user_id: UUID) -> User:
    # Pure: the id is generated outside (IdGeneratorProtocol) and passed in.
    return User(id=user_id, email=data.email, name=data.name)


def to_user_record(user: User) -> UserRecord:
    return UserRecord(id=str(user.id), email=user.email, name=user.name)


def to_user_query_params(record: UserRecord) -> dict[str, Any]:
    return record.model_dump()


def to_user_records(rows: list[dict[str, Any]]) -> list[UserRecord]:
    return [UserRecord(**row) for row in rows]


def to_single_user_record(records: list[UserRecord]) -> Result[UserRecord, UserError]:
    # A write that returns no row is a storage failure, not a crash.
    return Maybe.from_optional(next(iter(records), None)).map(Success).value_or(Failure(UserError.STORAGE_FAILURE))


def to_user_from_record(record: UserRecord) -> User:
    return User(id=UUID(record.id), email=record.email, name=record.name)


def to_storage_error(_: Exception) -> UserError:
    return UserError.STORAGE_FAILURE


def to_create_user_output(user: User) -> CreateUserOutput:
    return CreateUserOutput(id=str(user.id), email=user.email, name=user.name)


def to_create_user_outcome(result: Result[CreateUserOutput, UserError]) -> CreateUserOutcome:
    """The only Result -> schema conversion of the use case; everything after works on the outcome."""
    return (
        result.map(lambda output: CreateUserOutcome(output=output))
        .lash(lambda error: Success(CreateUserOutcome(error=error)))
        .unwrap()
    )


def to_create_user_response(status: int, outcome: CreateUserOutcome) -> CreateUserResponse:
    body = (
        Maybe.from_optional(outcome.output)
        .map(lambda output: output.model_dump())
        .or_else_call(lambda: {"error": outcome.error, "message": USER_ERROR_MESSAGES[outcome.error]})
    )
    return CreateUserResponse(status=status, body=body)


def to_create_user_log_entry(outcome: CreateUserOutcome) -> LogEntry:
    return (
        Maybe.from_optional(outcome.output)
        .map(lambda output: LogEntry(level="info", message="user created", context={"user_id": output.id}))
        .or_else_call(lambda: LogEntry(level="error", message="could not create user", context={"error": outcome.error}))
    )
