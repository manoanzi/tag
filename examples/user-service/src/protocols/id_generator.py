from typing import Protocol
from uuid import UUID


class IdGeneratorProtocol(Protocol):
    """Randomness is a side effect: it lives behind a Protocol, like a clock would."""

    def new_id(self) -> UUID: ...
