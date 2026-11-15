from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class UserError(StrEnum):
    """Every way the use case can fail. The value is the public message."""

    INVALID_PAYLOAD = "Invalid payload"
    EMAIL_DOMAIN_NOT_ALLOWED = "Email domain not allowed"
    USER_ALREADY_EXISTS = "A user with this email already exists"
    STORAGE_FAILURE = "Could not access user storage"


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
    model_config = ConfigDict(frozen=True)

    email: EmailStr
    name: str


class CreateUserOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    email: str
    name: str
