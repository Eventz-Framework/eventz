from __future__ import annotations

from eventz.event_bus import EventBus
from eventz.immutable import Immutable
from eventz.messages import Event


class ExampleEvent(Event):
    version: int = 1

    def __init__(
        self, property_one: str
    ):
        super().__init__()
        self.property_one = property_one


class Model(metaclass=Immutable):
    def __init__(self, property_one: str, property_two: int):
        self.property_one: str = property_one
        self.property_two: int = property_two

    def increment(self) -> Model:
        return Immutable.__mutate__(self, "property_two", self.property_two + 1)

    def trigger_example_event(self):
        event = ExampleEvent(
            property_one=self.property_one
        )
        EventBus.send(event)


class PrivateModel(metaclass=Immutable):
    def __init__(self, property_one: str, property_two: int):
        self.property_one: str = property_one
        self.property_two: int = property_two

    def increment(self) -> PrivateModel:
        return Immutable.__mutate__(self, "property_two", self.property_two + 1)


def test_that_value_objects_using_mutate_maintain_immutable_state():
    model1 = Model(property_one="A", property_two=1)
    model2 = model1.increment()
    assert model1 is not model2
    assert model1.property_two == 1
    assert model2.property_two == 2
    assert model1 is not model2
