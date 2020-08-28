from __future__ import annotations
import pytest

from eventz.value_object import ValueObject


class Model(ValueObject):
    def __init__(self, property_one: str, property_two: int):
        super().__init__()
        self.property_one: str = property_one
        self.property_two: int = property_two

    def increment(self) -> Model:
        return self._mutate("property_two", self.property_two + 1)


class Child(Model):
    def __init__(self, property_one: str, property_two: int):
        super().__init__(property_one, property_two)


def test_that_value_objects_created_with_the_same_attributes_are_not_the_same():
    model1 = Model(property_one="A", property_two=1)
    model2 = Model(property_one="A", property_two=1)
    model3 = Model(property_one="B", property_two=2)
    assert model1 is not model2
    assert model2 is not model3


def test_that_value_objects_created_with_the_same_attributes_are_equal():
    model1 = Model(property_one="A", property_two=1)
    model2 = Model(property_one="A", property_two=1)
    model3 = Model(property_one="B", property_two=2)
    assert model1 == model2
    assert model2 != model3


def test_that_inherited_value_objects_created_with_the_same_attributes_are_equal():
    model1 = Model(property_one="A", property_two=1)
    model2 = Model(property_one="B", property_two=2)
    child = Child(property_one="A", property_two=1)
    assert model1 == child
    assert model2 != child


def test_equality_checks_against_other_types():
    model1 = Model(property_one="A", property_two=1)
    assert (model1 == 1) is False
    assert model1 != 1


def test_repr():
    model1 = Model(property_one="A", property_two=1)
    assert repr(model1) == "Model(property_one=A property_two=1)"


def test_mutation():
    model1 = Model(property_one="A", property_two=1)
    assert model1.increment() == Model(property_one="A", property_two=2)


def test_that_value_objects_are_immutable():
    model = Model(property_one="A", property_two=1)
    with pytest.raises(AttributeError):
        model.property_one = "B"
