from typing import Protocol, Tuple

from eventz.messages import Event


class EventStoreProtocol(Protocol):  # pragma: no cover
    def fetch(self, aggregate_id: str) -> Tuple[Event, ...]:
        ...

    def persist(self, aggregate_id: str, events: Tuple[Event, ...]) -> None:
        ...
