from typing import Any

from src.domains.user import CreateUserResponse
from src.flows.user.create_user_flow import create_user_flow
from src.protocols.database import DatabaseProtocol
from src.protocols.http_server import HttpServerProtocol
from src.protocols.id_generator import IdGeneratorProtocol
from src.protocols.logger import LoggerProtocol


def handle_create_user(
    db: DatabaseProtocol, ids: IdGeneratorProtocol, logger: LoggerProtocol, raw_body: dict[str, Any]
) -> CreateUserResponse:
    return create_user_flow(db, ids, logger, raw_body)


def register_user_handlers(
    http: HttpServerProtocol, db: DatabaseProtocol, ids: IdGeneratorProtocol, logger: LoggerProtocol
) -> None:
    http.post("/users", lambda body: handle_create_user(db, ids, logger, body))
