from __future__ import annotations

from eventz.immutable import Immutable
from eventz.messages import Event


class ExampleEvent(Event):
    version: int = 1

    def __init__(self, property_one: str):
        super().__init__()
        self.property_one = property_one


class Model(metaclass=Immutable):
    def __init__(self, property_one: str, property_two: int):
        self.property_one: str = property_one
        self.property_two: int = property_two

    def increment(self) -> Model:
        return Immutable.__mutate__(self, "property_two", self.property_two + 1)


class PrivateModel(metaclass=Immutable):
    transform_underscores: bool = True

    def __init__(self, property_one: int):
        self._property_one: int = property_one

    def increment(self) -> PrivateModel:
        return Immutable.__mutate__(
            self, "_property_one", self._property_one + 1, self.transform_underscores
        )

    @property
    def property_one(self) -> int:
        return self._property_one


def test_that_value_objects_using_mutate_maintain_immutable_state():
    model1 = Model(property_one="A", property_two=1)
    model2 = model1.increment()
    assert model1 is not model2
    assert model1.property_two == 1
    assert model2.property_two == 2
    assert model1 is not model2


def test_that_model_with_private_fields_mutates_correctly():
    model1 = PrivateModel(property_one=122)
    model2 = model1.increment()
    assert model2.property_one == 123
