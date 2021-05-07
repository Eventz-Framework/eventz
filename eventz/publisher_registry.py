from typing import Dict, Tuple

from eventz.packets import Packet
from eventz.protocols import PublisherProtocol, PublisherRegistryProtocol


class PublisherRegistry(PublisherRegistryProtocol):
    def __init__(self):
        self._publishers: Dict[str, PublisherProtocol] = {}

    def register(self, publisher_name: str, publisher: PublisherProtocol) -> None:
        self._publishers[publisher_name] = publisher

    def get_publishers(self) -> Tuple[PublisherProtocol]:
        return tuple(self._publishers.values())

    def get_publisher(self, publisher_name: str) -> PublisherProtocol:
        return self._publishers[publisher_name]

    def publish(self, packet: Packet) -> None:
        for publisher in self._publishers.values():
            publisher.publish(packet)
