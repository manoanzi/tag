from typing import Any

from returns.functions import tap

from src.adapters.user_adapter import to_create_user_input, to_create_user_response_body
from src.flows.user.create_user_flow import create_user_flow
from src.logics.user_logic import resolve_create_user_status
from src.protocols.database import DatabaseProtocol
from src.protocols.http_server import HttpServerProtocol
from src.protocols.id_generator import IdGeneratorProtocol
from src.protocols.logger import LoggerProtocol


def handle_create_user(
    db: DatabaseProtocol, ids: IdGeneratorProtocol, logger: LoggerProtocol, raw_body: dict[str, Any]
) -> tuple[int, dict[str, Any]]:
    result = to_create_user_input(raw_body).bind(lambda data: create_user_flow(db, ids, data))

    result.map(tap(lambda output: logger.info("user created", user_id=output.id))).alt(
        tap(lambda error: logger.error("could not create user", error=error.name))
    )

    return resolve_create_user_status(result), to_create_user_response_body(result)


def register_user_handlers(
    http: HttpServerProtocol, db: DatabaseProtocol, ids: IdGeneratorProtocol, logger: LoggerProtocol
) -> None:
    http.post("/users", lambda body: handle_create_user(db, ids, logger, body))
