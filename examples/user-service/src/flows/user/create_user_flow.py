from typing import Any

from returns.pipeline import flow
from returns.pointfree import bind, map_

from src.adapters.user_adapter import (
    to_create_user_input,
    to_create_user_log_entry,
    to_create_user_outcome,
    to_create_user_output,
    to_create_user_response,
    to_rule_result,
    to_user_domain,
    to_user_record,
)
from src.domains.user import CreateUserResponse
from src.gateways.log_gateway import write_log
from src.gateways.user_gateway import find_users_by_email, generate_user_id, persist_user
from src.logics.user_logic import check_email_domain, check_user_is_new, resolve_create_user_status
from src.protocols.database import DatabaseProtocol
from src.protocols.id_generator import IdGeneratorProtocol
from src.protocols.logger import LoggerProtocol


def create_user_flow(
    db: DatabaseProtocol, ids: IdGeneratorProtocol, logger: LoggerProtocol, raw: dict[str, Any]
) -> CreateUserResponse:
    result = to_create_user_input(raw).bind(  # Adapter (Tolerant Reader)
        lambda data: flow(
            to_rule_result(check_email_domain(data.email)),  # Logic + Adapter
            bind(lambda _: find_users_by_email(db, data.email)),  # Gateway (IO)
            bind(lambda existing: to_rule_result(check_user_is_new(existing))),  # Logic + Adapter
            bind(lambda _: generate_user_id(ids)),  # Gateway (randomness)
            map_(lambda user_id: to_user_domain(data, user_id)),  # Adapter
            map_(to_user_record),  # Adapter
            bind(lambda record: persist_user(db, record)),  # Gateway (IO)
            map_(to_create_user_output),  # Adapter
        )
    )
    write_log(logger, to_create_user_log_entry(result))  # Adapter + Gateway (IO)
    status = resolve_create_user_status(to_create_user_outcome(result))  # Adapter + Logic
    return to_create_user_response(status, result)  # Adapter
