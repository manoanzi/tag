from returns.pipeline import flow
from returns.pointfree import bind, map_
from returns.result import Result

from src.adapters.user_adapter import to_create_user_output, to_user_domain, to_user_record
from src.domains.user import CreateUserInput, CreateUserOutput, UserError
from src.gateways.user_gateway import find_users_by_email, generate_user_id, persist_user
from src.logics.user_logic import ensure_user_not_exists, validate_email_domain
from src.protocols.database import DatabaseProtocol
from src.protocols.id_generator import IdGeneratorProtocol


def create_user_flow(
    db: DatabaseProtocol, ids: IdGeneratorProtocol, data: CreateUserInput
) -> Result[CreateUserOutput, UserError]:
    return flow(
        validate_email_domain(data.email),  # Logic (pure)
        bind(lambda email: find_users_by_email(db, email)),  # Gateway (IO)
        bind(ensure_user_not_exists),  # Logic (pure)
        bind(lambda _: generate_user_id(ids)),  # Gateway (randomness)
        map_(lambda user_id: to_user_domain(data, user_id)),  # Adapter
        map_(to_user_record),  # Adapter
        bind(lambda record: persist_user(db, record)),  # Gateway (IO)
        map_(to_create_user_output),  # Adapter
    )
