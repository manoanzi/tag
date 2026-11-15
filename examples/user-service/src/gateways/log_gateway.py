from src.protocols.logger import LogEntry, LoggerProtocol


def write_log(logger: LoggerProtocol, entry: LogEntry) -> None:
    logger.log(entry)
