from __future__ import annotations

from typing import Protocol, TypeVar, Callable, Tuple, Any, Dict

from eventz.messages import Event, Command

T = TypeVar("T")


class ProcessesCommandsProtocol(Protocol):
    def process(self, command: Command) -> Tuple[Event, ...]:
        ...


class AppliesEventsProtocol(Protocol):
    def apply(self, event: Event) -> None:
        ...


class EmitsEventsProtocol(Protocol):
    def send(self, event: Event):
        ...


class RegistersEventHandlersProtocol(Protocol):
    def register_handler(self, name: str, handler: Callable):
        ...

    def deregister_handler(self, name: str):
        ...

    def list_handler_names(self) -> Tuple[str, ...]:
        ...

    def clear_handlers(self) -> None:
        ...


class EventBusProtocol(EmitsEventsProtocol, RegistersEventHandlersProtocol):
    pass


class MarshallProtocol(Protocol):
    def to_json(self, obj: Any) -> str:
        ...

    def from_json(self, json_string: str) -> Any:
        ...

    def register_codec(self, name: str, handler: MarshallCodecProtocol):
        ...

    def deregister_codec(self, name: str):
        ...


class MarshallCodecProtocol(Protocol):
    def serialise(self, obj: Any) -> Dict:
        ...

    def deserialise(self, params: Dict) -> Any:
        ...

    def handles(self, obj: Any) -> bool:
        ...


class JsonSerlialisable(Protocol):
    def get_json_data(self) -> Dict:
        ...
