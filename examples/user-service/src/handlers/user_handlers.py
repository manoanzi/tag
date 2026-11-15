from typing import Any

from pydantic import ValidationError
from returns.result import Failure, Success

from src.adapters.user_adapter import to_create_user_input
from src.flows.user.create_user_flow import create_user_flow
from src.protocols.database import DatabaseClient
from src.protocols.http_server import HttpServer
from src.protocols.logger import Logger


def handle_create_user(
    db: DatabaseClient, logger: Logger, raw_body: dict[str, Any]
) -> tuple[int, dict[str, Any]]:
    try:
        data = to_create_user_input(raw_body)
    except ValidationError as error:
        return 422, {"error": "invalid payload", "details": error.errors(include_url=False)}

    match create_user_flow(db, data):
        case Success(output):
            logger.info("user created", user_id=output.id)
            return 201, output.model_dump()
        case Failure(error):
            logger.error("could not create user", error=error)
            return 400, {"error": error}
    return 500, {"error": "unexpected result"}


def register_user_handlers(http: HttpServer, db: DatabaseClient, logger: Logger) -> None:
    http.post("/users", lambda body: handle_create_user(db, logger, body))
