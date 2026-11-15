from uuid import UUID, uuid4


class UUID4Driver:
    """Implements the IdGeneratorProtocol with random UUIDv4 values."""

    def new_id(self) -> UUID:
        return uuid4()
