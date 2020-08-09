from typing import Sequence, Protocol, Tuple

from eventz.messages import Event


class EventStoreProtocol(Protocol):
    def fetch(self, aggregate_id: str) -> Tuple[Event, ...]:
        ...

    def persist(self, aggregate_id: str, events: Sequence[Event]):
        ...
