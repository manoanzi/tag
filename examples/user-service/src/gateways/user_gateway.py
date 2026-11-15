from uuid import UUID

from returns.result import Result, Success

from src.adapters.user_adapter import to_query_params, to_storage_error, to_user_from_rows, to_user_records
from src.domains.user import User, UserError, UserRecord
from src.protocols.database import DatabaseProtocol
from src.protocols.id_generator import IdGeneratorProtocol
from src.resources.user_queries import FIND_USERS_BY_EMAIL, INSERT_USER


def find_users_by_email(db: DatabaseProtocol, email: str) -> Result[list[UserRecord], UserError]:
    return db.execute(FIND_USERS_BY_EMAIL, {"email": email}).map(to_user_records).alt(to_storage_error)


def persist_user(db: DatabaseProtocol, record: UserRecord) -> Result[User, UserError]:
    return db.execute(INSERT_USER, to_query_params(record)).map(to_user_from_rows).alt(to_storage_error)


def generate_user_id(ids: IdGeneratorProtocol) -> Result[UUID, UserError]:
    return Success(ids.new_id())
