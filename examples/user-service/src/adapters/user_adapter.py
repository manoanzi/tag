from typing import Any
from uuid import uuid4

from returns.result import safe

from src.domains.user import CreateUserInput, CreateUserOutput, User


@safe
def to_create_user_input(raw: dict[str, Any]) -> CreateUserInput:
    # Tolerant Reader: read only the fields this use case needs, ignore the rest.
    # Validation can fail, so @safe turns the exception into a Failure.
    return CreateUserInput(email=raw.get("email", ""), name=raw.get("name", ""))


def to_user_domain(data: CreateUserInput) -> User:
    return User(id=uuid4(), email=data.email, name=data.name)


def to_create_user_output(user: User) -> CreateUserOutput:
    return CreateUserOutput(id=str(user.id), email=user.email, name=user.name)
