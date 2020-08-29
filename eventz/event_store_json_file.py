import json
import os
import shutil
from typing import Sequence, Tuple

from eventz.event_store import EventStore
from eventz.messages import Event
from eventz.protocols import MarshallProtocol, EventStoreProtocol


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

    def fetch(self, aggregate_id: str) -> Tuple[Event, ...]:
        file_path = self._get_file_path(aggregate_id)
        if not os.path.isfile(file_path):
            return ()
        with open(file_path) as json_file:
            json_string = json_file.read()
        return tuple(self._marshall.from_json(json_string))

    def persist(self, aggregate_id: str, events: Sequence[Event]):
        if not os.path.isdir(self._storage_path):
            os.mkdir(self._storage_path)
        with open(f"{self._storage_path}/{aggregate_id}.json", "w+") as json_file:
            json.dump(self._marshall.to_json(events), json_file)

    def _get_file_path(self, aggregate_id: str) -> str:
        return f"{self._storage_path}/{aggregate_id}.json"
