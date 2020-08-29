from __future__ import annotations

from typing import Protocol, TypeVar, Tuple, Any, Dict

from eventz.messages import Event, Command

T = TypeVar("T")
Events = Tuple[Event, ...]


class ProcessesCommandsProtocol(Protocol):  # pragma: no cover
    def process(self, command: Command) -> Events:
        ...


class RepositoryProtocol(Protocol[T]):  # pragma: no cover
    def create(self, **kwargs) -> Events:
        ...

    def read(self, aggregate_id: str) -> T:
        ...

    def persist(self, aggregate_id: str, events: Events) -> None:
        ...


class AggregateBuilderProtocol(Protocol[T]):  # pragma: no cover
    def create(self, events: Events) -> T:
        ...

    def update(self, aggregate: T, events: Events) -> T:
        ...


class MarshallProtocol(Protocol):  # pragma: no cover
    def to_json(self, obj: Any) -> str:
        ...

    def from_json(self, json_string: str) -> Any:
        ...

    def register_codec(self, name: str, handler: MarshallCodecProtocol):
        ...

    def deregister_codec(self, name: str):
        ...


class MarshallCodecProtocol(Protocol):  # pragma: no cover
    def serialise(self, obj: Any) -> Dict:
        ...

    def deserialise(self, params: Dict) -> Any:
        ...

    def handles(self, obj: Any) -> bool:
        ...


class JsonSerlialisable(Protocol):  # pragma: no cover
    def get_json_data(self) -> Dict:
        ...


class EventStoreProtocol(Protocol):  # pragma: no cover
    def fetch(self, aggregate_id: str) -> Events:
        ...

    def persist(self, aggregate_id: str, events: Events) -> None:
        ...