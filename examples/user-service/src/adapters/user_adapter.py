from typing import Any
from uuid import UUID

from returns.result import Result, Success, safe

from src.domains.user import CreateUserInput, CreateUserOutput, User, UserError, UserRecord


def to_create_user_input(raw: dict[str, Any]) -> Result[CreateUserInput, UserError]:
    # Tolerant Reader: read only the fields this use case needs, ignore the rest.
    return _parse_create_user_input(raw).alt(lambda _: UserError.INVALID_PAYLOAD)


@safe
def _parse_create_user_input(raw: dict[str, Any]) -> CreateUserInput:
    return CreateUserInput(email=raw.get("email", ""), name=raw.get("name", ""))


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


def to_create_user_response_body(result: Result[CreateUserOutput, UserError]) -> dict[str, Any]:
    return (
        result.map(lambda output: output.model_dump())
        .lash(lambda error: Success({"error": error.name.lower(), "message": error.value}))
        .unwrap()
    )
