from typing import Dict, TypedDict

from eventz.packets import Packet
from eventz.protocols import EventParserProtocol


class SimpleEvent(TypedDict):
    connection_id: str
    route: str
    msgid: str
    dialog: str
    payload: Dict


class EventParserDummy(EventParserProtocol[SimpleEvent]):
    def get_command_packet(self, event: SimpleEvent) -> Packet:
        return Packet(
            subscribers=(event["connection_id"],),
            message_type="COMMAND",
            route=event["route"],
            msgid=event["msgid"],
            dialog=event["dialog"],
            seq=1,
            options=None,
            payload=event["payload"],
        )
