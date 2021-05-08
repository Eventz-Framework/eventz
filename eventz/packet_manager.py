from typing import List, Optional, Tuple

from eventz.aggregate import Aggregate
from eventz.messages import Event
from eventz.packets import Packet
from eventz.protocols import PacketManagerProtocol


class PacketManager(PacketManagerProtocol):
    def __init__(self):
        self._is_broadcast: bool = False
        self._command_packet: Optional[Packet] = None
        self._other_subscribers: Tuple[str, ...] = tuple()

    def init_dialog(
        self,
        command_packet: Packet,
        other_subscribers: Tuple[str, ...],
    ):
        self._command_packet = command_packet
        if self._is_broadcast_command(self._command_packet):
            self._is_broadcast = True
            self._other_subscribers = other_subscribers

    def get_broadcast_command_packet(self) -> Optional[Packet]:
        if self._is_broadcast and self._other_subscribers:
            return Packet(
                subscribers=self._other_subscribers,
                message_type="COMMAND",
                route=self._command_packet.route,
                msgid=self._command_packet.msgid,
                dialog=self._command_packet.dialog,
                seq=1,
                options=None,
                payload=self._command_packet.payload,
            )
        return None

    def get_ack_packet(self) -> Packet:
        return Packet(
            subscribers=self._command_packet.subscribers + self._other_subscribers,
            message_type="ACK",
            route=self._command_packet.route,
            msgid=Aggregate.make_id(),
            dialog=self._command_packet.dialog,
            seq=2,
            options=None,
            payload=None,
        )

    def get_next_event_packet(self, event: Event, event_packets_sent: List[Packet]) -> Packet:
        return Packet(
            subscribers=self._command_packet.subscribers + self._other_subscribers,
            message_type="EVENT",
            route=self._command_packet.route,
            msgid=Aggregate.make_id(),
            dialog=self._command_packet.dialog,
            seq=len(event_packets_sent) + 3,
            options=None,
            payload=event,
        )

    def get_done_event_packet(self, event_packets_sent: List[Packet]) -> Packet:
        return Packet(
            subscribers=self._command_packet.subscribers + self._other_subscribers,
            message_type="DONE",
            route=self._command_packet.route,
            msgid=Aggregate.make_id(),
            dialog=self._command_packet.dialog,
            seq=len(event_packets_sent) + 3,
            options=None,
            payload=tuple(e.msgid for e in event_packets_sent),
        )

    def _is_broadcast_command(self, command_packet: Packet) -> bool:
        return command_packet.payload.get("__fqn__") not in [
            "commands.eventz.ReplayCommand",
        ]
