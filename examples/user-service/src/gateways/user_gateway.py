from typing import Any

from returns.result import Result

from src.domains.user import User
from src.protocols.database import DatabaseClient
from src.resources.user_queries import FIND_USER_BY_EMAIL, INSERT_USER


def find_user_by_email(db: DatabaseClient, email: str) -> Result[list[dict[str, Any]], str]:
    return db.execute(FIND_USER_BY_EMAIL, {"email": email}).alt(str)


def persist_user(db: DatabaseClient, user: User) -> Result[User, str]:
    return db.execute(INSERT_USER, user.model_dump(mode="json")).map(lambda _: user).alt(str)
