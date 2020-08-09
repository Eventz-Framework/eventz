from typing import Callable, Tuple

from eventz.messages import Event
from eventz.protocols import EventBusProtocol


class EventBus:
    """
    Thin wrapper around the EventBusProtocol interface.
    Allows EventBus to be used statically/globally throughout the codebase
    whilst still keeping the actual implementation decoupled.
    """
    _implementation: EventBusProtocol = None

    @classmethod
    def set_implementation(cls, implementation: EventBusProtocol):
        cls._implementation = implementation

    @classmethod
    def send(cls, event: Event):
        return cls._implementation.send(event)

    @classmethod
    def register_handler(cls, name: str, handler: Callable):
        return cls._implementation.register_handler(name, handler)

    @classmethod
    def deregister_handler(cls, name: str):
        return cls._implementation.deregister_handler(name)

    @classmethod
    def list_handler_names(cls) -> Tuple[str, ...]:
        return cls._implementation.list_handler_names()

    @classmethod
    def clear_handlers(cls) -> None:
        return cls._implementation.clear_handlers()
