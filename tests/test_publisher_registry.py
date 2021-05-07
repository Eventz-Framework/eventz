from eventz.packets import Packet
from eventz.protocols import PublisherProtocol
from eventz.publisher_registry import PublisherRegistry


class DummyPublisherA(PublisherProtocol):
    def publish(self, packet: Packet) -> None:
        return None


class DummyPublisherB(PublisherProtocol):
    def publish(self, packet: Packet) -> None:
        return None


def test_publishers_are_returned_after_registration():
    dummy_publisher_a = DummyPublisherA()
    dummy_publisher_b = DummyPublisherB()
    publisher_registry = PublisherRegistry()
    publisher_registry.register("DummyA", dummy_publisher_a)
    publisher_registry.register("DummyB", dummy_publisher_b)
    publisher_registry.register("DummyA", dummy_publisher_a)
    assert publisher_registry.get_publishers() == (
        dummy_publisher_a,
        dummy_publisher_b,
    )
    assert publisher_registry.get_publisher("DummyA") == dummy_publisher_a
    assert publisher_registry.get_publisher("DummyB") == dummy_publisher_b
