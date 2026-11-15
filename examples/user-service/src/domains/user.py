from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class User(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID
    email: EmailStr
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
