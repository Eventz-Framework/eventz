import pytest

from eventz.entity import Entity


class Model(Entity):
    def __init__(self, property_one: str, property_two: int):
        super().__init__()
        self.property_one: str = property_one
        self.property_two: int = property_two


def test_that_an_entity_generates_a_unique_id_when_created():
    model1 = Model(property_one="A", property_two=1)
    model2 = Model(property_one="A", property_two=1)
    assert model1.uuid != model2.uuid


def test_that_an_entity_id_is_immutable():
    model1 = Model(property_one="A", property_two=1)
    with pytest.raises(AttributeError):
        model1.uuid = "new_id"


def test_that_entities_created_with_the_same_attributes_are_the_not_same():
    model1 = Model(property_one="A", property_two=1)
    model2 = Model(property_one="A", property_two=1)
    model3 = Model(property_one="B", property_two=2)
    assert model1 is not model2
    assert model2 is not model3


def test_that_entities_created_with_the_same_attributes_are_not_equal():
    model1 = Model(property_one="A", property_two=1)
    model2 = Model(property_one="A", property_two=1)
    model3 = Model(property_one="B", property_two=2)
    assert model1 != model2
    assert model2 != model3
