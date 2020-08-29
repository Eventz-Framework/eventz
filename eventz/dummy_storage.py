from typing import Dict

from eventz.protocols import Events, EventStoreProtocol


class DummyStorage(EventStoreProtocol):
    def __init__(self):
        self._persisted_events: Dict[str, Events] = {}
        self._fetch_called: int = 0

    def fetch(self, aggregate_id: str) -> Events:
        self._fetch_called += 1
        return self._persisted_events[aggregate_id]

    def persist(self, aggregate_id: str, events: Events):
        if aggregate_id in self._persisted_events:
            self._persisted_events[aggregate_id] = (
                self._persisted_events[aggregate_id] + events
            )
        else:
            self._persisted_events[aggregate_id] = events

    @property
    def fetch_called(self) -> int:
        return self._fetch_called
