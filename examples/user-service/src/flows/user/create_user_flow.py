from returns.pipeline import flow
from returns.pointfree import bind, map_
from returns.result import Result, Success

from src.adapters.user_adapter import to_create_user_output, to_user_domain
from src.domains.user import CreateUserInput, CreateUserOutput
from src.gateways.user_gateway import find_user_by_email, persist_user
from src.logics.user_logic import ensure_user_not_exists, validate_email_domain
from src.protocols.database import DatabaseClient


def create_user_flow(db: DatabaseClient, data: CreateUserInput) -> Result[CreateUserOutput, str]:
    return flow(
        validate_email_domain(data.email),
        bind(lambda email: find_user_by_email(db, email)),
        bind(ensure_user_not_exists),
        bind(lambda _: Success(to_user_domain(data))),
        bind(lambda user: persist_user(db, user)),
        map_(to_create_user_output),
    )
