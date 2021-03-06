from __future__ import annotations

from typing import List, Optional, Protocol, TypeVar, Tuple, Any, Dict
from datetime import datetime

from eventz.messages import Event, Command
from eventz.packets import Packet

T = TypeVar("T")
Events = Tuple[Event, ...]


class ServiceProtocol(Protocol):  # pragma: no cover
    def process(self, command: Command) -> Events:
        ...

    def domain_command_from_packet(self, command_packet: Packet) -> Command:
        ...


class RepositoryProtocol(Protocol[T]):  # pragma: no cover
    def create(self, **kwargs) -> Events:
        ...

    def read(self, aggregate_id: str) -> Tuple[T, int]:
        ...

    def persist(self, aggregate_id: str, events: Events) -> Events:
        ...

    def fetch_all_from(self, aggregate_id: str, seq: Optional[int] = None) -> Events:
        ...

    def get_builder(self) -> AggregateBuilderProtocol:
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

    def serialise_data(self, data: Any) -> Any:
        ...

    def deserialise_data(self, data: Any) -> Any:
        ...

    def register_codec(self, name: str, handler: MarshallCodecProtocol):
        ...

    def deregister_codec(self, name: str):
        ...

    def transform_keys_serialisation(self, data) -> Any:
        ...

    def transform_keys_deserialisation(self, data) -> Any:
        ...


class MarshallCodecProtocol(Protocol):  # pragma: no cover
    def serialise(self, obj: Any, marshall: MarshallProtocol) -> Dict:
        ...

    def deserialise(self, params: Dict, marshall: MarshallProtocol) -> Any:
        ...

    def handles(self, obj: Any) -> bool:
        ...


class JsonSerlialisable(Protocol):  # pragma: no cover
    def get_json_data(self) -> Dict:
        ...


class EventStoreProtocol(Protocol):  # pragma: no cover
    def fetch(self, aggregate_id: str, seq: Optional[int] = None) -> Events:
        ...

    def persist(self, aggregate_id: str, events: Events) -> Events:
        ...


class SubscriptionRegistryProtocol(Protocol[T]):
    def register(
        self, aggregate_id: str, subscription: T, time: Optional[datetime] = None
    ) -> None:
        ...

    def deregister(
        self, subscription: T
    ) -> None:
        ...

    def fetch(self, aggregate_id: str) -> Tuple[T]:
        ...


class ServiceRegistryProtocol(Protocol):
    def register(self, service_name: str, service: ServiceProtocol) -> None:
        ...

    def get_service(self, service_name: str) -> ServiceProtocol:
        ...


class PublisherProtocol(Protocol):
    def publish(self, packet: Packet) -> None:
        ...


class PublisherRegistryProtocol(Protocol):
    def register(self, publisher_name: str, publisher: PublisherProtocol) -> None:
        ...

    def get_publishers(self) -> Tuple[PublisherProtocol]:
        ...

    def get_publisher(self, publisher_name: str) -> PublisherProtocol:
        ...

    def publish(self, packet: Packet) -> None:
        ...


class PacketManagerProtocol(Protocol):
    def init_dialog(
        self, command_packet: Packet, other_subscribers: Tuple[str, ...],
    ):
        ...

    def get_broadcast_command_packet(self) -> Optional[Packet]:
        ...

    def get_ack_packet(self) -> Packet:
        ...

    def get_next_event_packet(
        self, event: Event, event_packets_sent: List[Packet]
    ) -> Packet:
        ...

    def get_done_event_packet(self, event_packets_sent: List[Packet]) -> Packet:
        ...


class EventParserProtocol(Protocol[T]):
    def get_command_packet(self, event: T) -> Packet:
        ...


class EventBrokerProtocol(Protocol):
    def handle(self, command_packet: Packet) -> None:
        ...

    def get_publisher(self, publisher_name: str) -> PublisherProtocol:
        ...
