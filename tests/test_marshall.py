import json
from datetime import datetime
from typing import List, Dict

from eventz.marshall import Marshall, DatetimeCodec
from eventz.value_object import ValueObject


class SimpleTypeEntity(ValueObject):
    def __init__(
            self, name: str, numbers: List[int],
    ):
        self.name: str = name
        self.numbers: List[int] = numbers


class ValueType(ValueObject):
    def __init__(self, name: str):
        self.name: str = name


class ComplexTypeEntity(ValueObject):
    def __init__(
            self, one: ValueType, two: ValueType,
    ):
        self.one: ValueType = one
        self.two: ValueType = two


class CustomTypeEntity(ValueObject):
    def __init__(
            self, name: str, timestamp: datetime,
    ):
        self.name: str = name
        self.timestamp: datetime = timestamp


class JsonSerialisableEntity(ValueObject):
    def __init__(self, public):
        self._private = public

    def get_json_data(self) -> Dict:
        return {
            "public": self._private
        }


numbers1 = [1, 2, 3, 4, 5]
numbers2 = [2, 3, 4, 5, 6]
numbers3 = [3, 4, 5, 6, 7]


def test_single_message_serialisation_to_json():
    entity1 = SimpleTypeEntity(name="Event One", numbers=numbers1)
    marshall = Marshall()
    assert marshall.to_json(entity1) == json.dumps(
        _make_simple_dict("Event One", numbers1)
    )


def test_single_message_deserialisation_from_json():
    marshall = Marshall()
    json_string = json.dumps(_make_simple_dict("Event One", numbers1))
    assert marshall.from_json(json_string) == SimpleTypeEntity(
        name="Event One", numbers=numbers1
    )


def test_sequence_of_messages_serialised_to_json():
    list_of_entities = [
        SimpleTypeEntity(name="Event One", numbers=numbers1),
        SimpleTypeEntity(name="Event Two", numbers=numbers2),
        SimpleTypeEntity(name="Event Three", numbers=numbers3),
    ]
    marshall = Marshall()
    assert marshall.to_json(list_of_entities) == json.dumps(
        [
            _make_simple_dict("Event One", numbers1),
            _make_simple_dict("Event Two", numbers2),
            _make_simple_dict("Event Three", numbers3),
        ]
    )


def test_sequence_of_messages_deserialised_from_json():
    marshall = Marshall()
    json_string = json.dumps(
        [
            _make_simple_dict("Event One", numbers1),
            _make_simple_dict("Event Two", numbers2),
            _make_simple_dict("Event Three", numbers3),
        ]
    )
    assert marshall.from_json(json_string) == [
        SimpleTypeEntity(name="Event One", numbers=numbers1),
        SimpleTypeEntity(name="Event Two", numbers=numbers2),
        SimpleTypeEntity(name="Event Three", numbers=numbers3),
    ]


def test_complex_object_serialised_to_json():
    entity1 = ComplexTypeEntity(
        one=ValueType(name="Value One"), two=ValueType(name="Value Two"),
    )
    marshall = Marshall()
    assert marshall.to_json(entity1) == json.dumps(
        _make_complex_dict("Value One", "Value Two")
    )


def test_complex_object_deserialised_from_json():
    json_string = json.dumps(_make_complex_dict("Value One", "Value Two"))
    marshall = Marshall()
    assert marshall.from_json(json_string) == ComplexTypeEntity(
        one=ValueType(name="Value One"), two=ValueType(name="Value Two")
    )


def test_entity_with_custom_datetime_handler_serialised_to_json():
    entity_name = "Entity One"
    dt1 = datetime(2020, 1, 2, 3, 4, 5, 123456)
    iso_dt1 = "2020-01-02T03:04:05.123456"
    entity1 = CustomTypeEntity(name=entity_name, timestamp=dt1)
    marshall = Marshall()
    marshall.register_codec(fcn="eventz.marshall.DatetimeCodec", codec=DatetimeCodec())
    assert marshall.to_json(entity1) == json.dumps(
        _make_with_datetime_dict(name=entity_name, iso_dt=iso_dt1)
    )


def test_entity_with_custom_datetime_handler_deserialised_from_json():
    entity_name = "Entity One"
    iso_dt1 = "2020-01-02T03:04:05.123456"
    dt1 = datetime(2020, 1, 2, 3, 4, 5, 123456)
    json_string = json.dumps(_make_with_datetime_dict(name=entity_name, iso_dt=iso_dt1))
    marshall = Marshall()
    marshall.register_codec(fcn="eventz.marshall.DatetimeCodec", codec=DatetimeCodec())
    assert marshall.from_json(json_string) == CustomTypeEntity(
        name=entity_name, timestamp=dt1
    )


def test_json_serialisable_class_to_json():
    value = 123
    entity = JsonSerialisableEntity(public=value)
    json_data = {"__fcn__": "tests.test_marshall.JsonSerialisableEntity", "public": 123}
    marshall = Marshall()
    assert marshall.to_json(entity) == json.dumps(json_data)


def test_json_serialisable_class_from_json():
    value = 123
    entity = JsonSerialisableEntity(public=value)
    json_data = {"__fcn__": "tests.test_marshall.JsonSerialisableEntity", "public": 123}
    marshall = Marshall()
    assert marshall.from_json(json.dumps(json_data)) == entity


def _make_simple_dict(name, numbers):
    return {
        "__fcn__": "tests.test_marshall.SimpleTypeEntity",
        "name": name,
        "numbers": numbers,
    }


def _make_complex_dict(name1, name2):
    return {
        "__fcn__": "tests.test_marshall.ComplexTypeEntity",
        "one": {"__fcn__": "tests.test_marshall.ValueType", "name": name1, },
        "two": {"__fcn__": "tests.test_marshall.ValueType", "name": name2, },
    }


def _make_with_datetime_dict(name, iso_dt):
    return {
        "__fcn__": "tests.test_marshall.CustomTypeEntity",
        "name": name,
        "timestamp": {
            "__codec__": "eventz.marshall.DatetimeCodec",
            "params": {"timestamp": iso_dt},
        },
    }
