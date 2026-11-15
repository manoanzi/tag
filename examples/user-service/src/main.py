from drivers.fastapi_driver import FastAPIDriver
from drivers.sqlite_driver import SQLiteDriver
from drivers.stdout_logger_driver import StdoutLoggerDriver
from drivers.uuid_driver import UUID4Driver
from src.handlers.user_handlers import register_user_handlers
from src.resources.settings import Settings, load_settings


def create_app(settings: Settings | None = None) -> FastAPIDriver:
    settings = settings or load_settings()

    db = SQLiteDriver(settings)
    ids = UUID4Driver()
    logger = StdoutLoggerDriver()
    http = FastAPIDriver()

    register_user_handlers(http, db, ids, logger)
    return http


def main() -> None:
    settings = load_settings()
    create_app(settings).start(port=settings.http_port)


if __name__ == "__main__":
    main()
