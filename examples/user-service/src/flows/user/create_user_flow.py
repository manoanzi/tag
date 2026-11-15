from typing import Any

from returns.pipeline import flow
from returns.pointfree import bind, map_

from src.adapters.user_adapter import (
    to_create_user_input,
    to_create_user_outcome,
    to_create_user_output,
    to_create_user_response,
    to_rule_result,
    to_user_domain,
    to_user_record,
)
from src.domains.user import CreateUserResponse
from src.gateways.user_gateway import find_users_by_email, persist_user
from src.logics.user_logic import (
    check_email_domain,
    check_user_is_new,
    resolve_create_user_log_level,
    resolve_create_user_status,
)
from src.protocols.database import DatabaseProtocol
from src.protocols.id_generator import IdGeneratorProtocol
from src.protocols.logger import LogEntry, LoggerProtocol


def create_user_flow(
    db: DatabaseProtocol, ids: IdGeneratorProtocol, logger: LoggerProtocol, raw: dict[str, Any]
) -> CreateUserResponse:
    result = to_create_user_input(raw).bind(  # Adapter (Tolerant Reader)
        lambda data: flow(
            to_rule_result(check_email_domain(data.email)),  # Logic + Adapter
            bind(lambda _: find_users_by_email(db, data.email)),  # Gateway (IO)
            bind(lambda existing: to_rule_result(check_user_is_new(existing))),  # Logic + Adapter
            map_(lambda _: to_user_domain(data, ids.new_id())),  # Protocol (randomness) + Adapter
            map_(to_user_record),  # Adapter
            bind(lambda record: persist_user(db, record)),  # Gateway (IO)
            map_(to_create_user_output),  # Adapter
        )
    )
    outcome = to_create_user_outcome(result)  # Adapter: Result -> schema, once
    status = resolve_create_user_status(outcome)  # Logic
    logger.log(  # Protocol (IO): one structured event per use case, values already decided
        LogEntry(
            level=resolve_create_user_log_level(outcome),  # Logic
            message="create user",
            context={"status": status, "error": outcome.error},
        )
    )
    return to_create_user_response(status, outcome)  # Adapter
