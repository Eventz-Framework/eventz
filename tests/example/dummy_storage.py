from typing import Sequence, Tuple, Optional

from eventz.event_store.event_store_protocol import EventStoreProtocol
from eventz.messages import Event


class DummyStorage(EventStoreProtocol):
    def __init__(self, fetched_events: Sequence[Event] = None):
        self._fetched_events: Sequence[Event] = fetched_events or tuple()
        self.persisted_events: Optional[Tuple[Event, ...]] = None
        self.fetch_called: int = 0

    def fetch(self, aggregate_id: str) -> Tuple[Event, ...]:
        self.fetch_called += 1
        return tuple(self._fetched_events)

    def persist(self, aggregate_id: str, events: Sequence[Event]):
        self.persisted_events = tuple(events)
