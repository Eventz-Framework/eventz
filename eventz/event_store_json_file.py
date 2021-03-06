import os
import shutil
from typing import Optional, Tuple

from eventz.event_store import EventStore
from eventz.messages import Event
from eventz.protocols import Events, MarshallProtocol, EventStoreProtocol


class EventStoreJsonFile(EventStore, EventStoreProtocol):
    def __init__(
        self,
        storage_path: str,
        marshall: MarshallProtocol,
        recreate_storage: bool = True,
    ):
        self._storage_path: str = storage_path
        self._marshall = marshall
        if recreate_storage and os.path.isdir(self._storage_path):
            shutil.rmtree(self._storage_path)
            os.mkdir(self._storage_path)
            # toy/example implementation, so don't worry about security
            os.chmod(self._storage_path, 0o777)

    def fetch(self, aggregate_id: str, seq: Optional[int] = None) -> Tuple[Event, ...]:
        file_path = self._get_file_path(aggregate_id)
        if not os.path.isfile(file_path):
            return ()
        with open(file_path) as json_file:
            json_string = json_file.read()
        slice_idx = self._get_slice_index(seq)
        return tuple(self._marshall.from_json(json_string)[slice_idx:])

    def _get_slice_index(self, seq: Optional[int]) -> int:
        slice_index = 0 if seq is None else seq - 1
        if slice_index < 0:
            return 0
        return slice_index

    def persist(self, aggregate_id: str, events: Events) -> Events:
        if not os.path.isdir(self._storage_path):
            os.mkdir(self._storage_path)
        existing_events = self.fetch(aggregate_id)
        persisted_events = tuple(
            e.sequence(idx + 1)
            for idx, e in enumerate(events)
        )
        with open(f"{self._storage_path}/{aggregate_id}.json", "w+") as json_file:
            json_file.write(self._marshall.to_json(existing_events + persisted_events))
        return tuple(persisted_events)

    def _get_file_path(self, aggregate_id: str) -> str:
        return f"{self._storage_path}/{aggregate_id}.json"
