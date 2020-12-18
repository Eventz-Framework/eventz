from __future__ import annotations
from typing import Tuple, Optional, Union, Dict, Iterable

from eventz.messages import Event
from eventz.value_object import ValueObject

Payload = Union[Dict, Event, Tuple[str]]


class Packet(ValueObject):
    def __init__(
        self,
        subscribers: Iterable[str],
        message_type: str,
        route: str,
        msgid: str,
        dialog: str,
        seq: int,
        options: Optional[Iterable[str]] = None,
        payload: Optional[Payload] = None,
    ):
        self.subscribers: Tuple[str] = tuple(subscribers)
        self.message_type: str = message_type
        self.route: str = route
        self.msgid: str = msgid
        self.dialog: str = dialog
        self.seq: int = seq
        self.options: Tuple[str] = tuple(options or [])
        self.payload: Optional[Payload] = payload

    def mutate(self, name, value) -> Packet:
        return self._mutate(name, value)
