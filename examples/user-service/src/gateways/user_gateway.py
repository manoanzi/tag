from returns.result import Result

from src.adapters.user_adapter import (
    to_storage_error,
    to_user_query_params,
    to_user_records,
)
from src.domains.user import UserError, UserRecord
from src.protocols.database import DatabaseProtocol

FIND_USERS_BY_EMAIL = """
    SELECT id, email, name FROM users WHERE email = :email
"""

INSERT_USER = """
    INSERT INTO users (id, email, name)
    VALUES (:id, :email, :name)
    RETURNING id, email, name
"""


def find_users_by_email(db: DatabaseProtocol, email: str) -> Result[list[UserRecord], UserError]:
    return db.execute(FIND_USERS_BY_EMAIL, {"email": email}).map(to_user_records).alt(to_storage_error)


def persist_user(db: DatabaseProtocol, record: UserRecord) -> Result[list[UserRecord], UserError]:
    return (
        db.execute(INSERT_USER, to_user_query_params(record))
        .alt(to_storage_error)
        .map(to_user_records)
    )

