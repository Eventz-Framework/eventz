from collections import Callable
from queue import SimpleQueue
from typing import Dict, Tuple

from eventz.messages import Event
from eventz.protocols import EventBusProtocol


class SubscriptionQueue:
    """
    FIFO subscription
    """
    def __init__(self):
        self._queue = SimpleQueue()

    def __call__(self, event: Event):
        self._queue.put(event)

    def get(self) -> Event:
        if not self._queue.empty():
            return self._queue.get()

    def all(self) -> Tuple[Event, ...]:
        events = []
        while not self._queue.empty():
            events.append(self._queue.get())
        return tuple(events)

    def __iter__(self):
        return self

    def __next__(self) -> Event:
        event = self.get()
        if event:
            return event
        raise StopIteration


class CollectAllHandler:
    def __init__(self, subscription: Callable):
        self._subscription: Callable = subscription

    def __call__(self, event: Event):
        self._subscription(event)


class OfTypeHandler:
    def __init__(self, subscription: Callable, of_type: type):
        self._subscription: Callable = subscription
        self._of_type: type = of_type

    def __call__(self, event: Event):
        if isinstance(event, self._of_type):
            self._subscription(event)


class EventBusDefault(EventBusProtocol):
    def __init__(self):
        self._handlers: Dict[str, Callable] = {}

    def send(self, event: Event):
        for handler in self._handlers.values():
            handler(event)

    def register_handler(self, name: str, handler: Callable):
        if name in self._handlers:
            err = f"Handler '{name}' already exists. Can't add it again."
            raise RuntimeError(err)
        self._handlers[name] = handler

    def deregister_handler(self, name: str):
        del self._handlers[name]

    def list_handler_names(self) -> Tuple[str, ...]:
        return tuple(self._handlers.keys())

    def clear_handlers(self) -> None:
        self._handlers = {}
