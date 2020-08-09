import pytest

from eventz.event_bus import EventBus
from eventz.event_bus_default import EventBusDefault


@pytest.fixture(autouse=True)
def setup():
    event_bus_default = EventBusDefault()
    EventBus.set_implementation(event_bus_default)
