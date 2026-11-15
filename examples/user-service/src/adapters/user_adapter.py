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
    # Tolerant Reader: read only the fields this use case needs, ignore the rest.
    return _parse_create_user_input(raw).alt(lambda _: UserError.INVALID_PAYLOAD)


@safe
def _parse_create_user_input(raw: dict[str, Any]) -> CreateUserInput:
    return CreateUserInput(email=raw.get("email", ""), name=raw.get("name", ""))


def to_rule_result(check: UserRuleCheck) -> Result[None, UserError]:
    """Turns a Logic decision (schema) into a step of the Result pipeline."""
    return Maybe.from_optional(check.error).map(Failure).value_or(Success(None))


def to_user_domain(data: CreateUserInput, user_id: UUID) -> User:
    # Pure: the id is generated outside (IdGeneratorProtocol) and passed in.
    return User(id=user_id, email=data.email, name=data.name)


def to_user_record(user: User) -> UserRecord:
    return UserRecord(id=str(user.id), email=user.email, name=user.name)


def to_query_params(record: UserRecord) -> dict[str, Any]:
    return record.model_dump()


def to_user_records(rows: list[dict[str, Any]]) -> list[UserRecord]:
    return [UserRecord(**row) for row in rows]


def to_user_from_rows(rows: list[dict[str, Any]]) -> User:
    return User(**rows[0])


def to_storage_error(_: Exception) -> UserError:
    return UserError.STORAGE_FAILURE


def to_create_user_output(user: User) -> CreateUserOutput:
    return CreateUserOutput(id=str(user.id), email=user.email, name=user.name)


def to_create_user_outcome(result: Result[CreateUserOutput, UserError]) -> CreateUserOutcome:
    return (
        result.map(lambda output: CreateUserOutcome(output=output))
        .lash(lambda error: Success(CreateUserOutcome(error=error)))
        .unwrap()
    )


def to_create_user_response(status: int, result: Result[CreateUserOutput, UserError]) -> CreateUserResponse:
    body = (
        result.map(lambda output: output.model_dump())
        .lash(lambda error: Success({"error": error.value, "message": USER_ERROR_MESSAGES[error]}))
        .unwrap()
    )
    return CreateUserResponse(status=status, body=body)


def to_create_user_log_entry(result: Result[CreateUserOutput, UserError]) -> LogEntry:
    return (
        result.map(lambda output: LogEntry(level="info", message="user created", context={"user_id": output.id}))
        .lash(
            lambda error: Success(
                LogEntry(level="error", message="could not create user", context={"error": error.value})
            )
        )
        .unwrap()
    )
