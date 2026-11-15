from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserError(StrEnum):
    """Every way the use case can fail. Public messages live in Resources."""

    INVALID_PAYLOAD = "invalid_payload"
    EMAIL_DOMAIN_NOT_ALLOWED = "email_domain_not_allowed"
    USER_ALREADY_EXISTS = "user_already_exists"
    STORAGE_FAILURE = "storage_failure"



class UserRuleCheck(BaseModel):
    """A business rule decision as data: no error means the rule passed."""

    model_config = ConfigDict(frozen=True)

    error: UserError | None = None

class User(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID
    email: EmailStr
    name: str


class UserRecord(BaseModel):
    """Persistence shape of a user: only primitive types."""

    model_config = ConfigDict(frozen=True)

    id: str
    email: str
    name: str


class CreateUserInput(BaseModel):
    """Unknown fields are ignored (Pydantic default); missing or empty ones are invalid."""

    model_config = ConfigDict(frozen=True)

    email: EmailStr
    name: str = Field(min_length=1)


class CreateUserOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    email: str
    name: str


class CreateUserResponse(BaseModel):
    """What the create-user use case answers to any transport."""

    model_config = ConfigDict(frozen=True)

    status: int
    body: dict[str, Any]


class CreateUserOutcome(BaseModel):
    """The end state of the use case, as data: either an output or an error."""

    model_config = ConfigDict(frozen=True)

    output: CreateUserOutput | None = None
    error: UserError | None = None
