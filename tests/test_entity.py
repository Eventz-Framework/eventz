from __future__ import annotations

from typing import Optional

import pytest

from eventz.entity import Entity


class Model(Entity):
    def __init__(
        self, property_one: str, property_two: int, uuid: Optional[str] = None
    ):
        super().__init__(uuid)
        self.property_one: str = property_one
        self.property_two: int = property_two

    def set_property_one_to_property_two(self) -> Model:
        return super()._mutate("property_one", str(self.property_two))

    def reset(self):
        return super()._mutate_all({
            "property_one": "",
            "property_two": 0,
        })



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


def test_equality_and_inequality():
    uuid = Entity.make_id()
    model1 = Model(property_one="A", property_two=1, uuid=uuid)
    model2 = Model(property_one="A", property_two=1, uuid=uuid)
    assert model1 == model2
    assert (model1 == 1) is False
    assert model1 != 1


def test_repr():
    uuid = Entity.make_id()
    model1 = Model(property_one="A", property_two=1, uuid=uuid)
    expected = f"Model(uuid={uuid} property_one=A property_two=1 __immutable__=True)"
    assert repr(model1) == expected


def test_mutate():
    model1 = Model(property_one="A", property_two=1)
    model2 = model1.set_property_one_to_property_two()
    assert model2.property_one == "1"


def test_mutate_all():
    model1 = Model(property_one="A", property_two=1)
    model2 = model1.reset()
    assert model2.property_one == ""
    assert model2.property_two == 0
