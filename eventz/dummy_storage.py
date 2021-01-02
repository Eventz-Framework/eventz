from collections import defaultdict
from typing import Dict, List, Optional

from eventz.messages import Event
from eventz.protocols import Events, EventStoreProtocol


class DummyStorage(EventStoreProtocol):
    def __init__(self):
        self._persisted_events: Dict[str, List[Event]] = defaultdict(list)
        self._fetch_called: int = 0

    def fetch(self, aggregate_id: str, msgid: Optional[str] = None) -> Events:
        self._fetch_called += 1
        return tuple(self._persisted_events[aggregate_id])

    def persist(self, aggregate_id: str, events: Events) -> Events:
        events_to_return = []
        for event in events:
            seq = len(self._persisted_events[aggregate_id]) + 1
            persisted_event = event.sequence(seq)
            events_to_return.append(persisted_event)
            self._persisted_events[aggregate_id].append(persisted_event)
        return tuple(events_to_return)

    @property
    def fetch_called(self) -> int:
        return self._fetch_called
