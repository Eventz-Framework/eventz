from typing import List

from eventz.packets import Packet
from eventz.protocols import PublisherProtocol


class PublisherDummy(PublisherProtocol):
    def __init__(self):
        self.published_packets: List[Packet] = []

    def publish(self, packet: Packet) -> None:
        self.published_packets.append(packet)
