import json
from datetime import datetime
from enum import Enum
from typing import List, Dict

import immutables
import pytest

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
        return {"public": self._private}


class Option(Enum):
    ONE = 1
    TWO = 2


class EnumEntity(ValueObject):
    def __init__(self, option: Option):
        self.option: Option = option


class MappingEntity(ValueObject):
    def __init__(self, mapping: immutables.Map):
        self.mapping = mapping


numbers1 = [1, 2, 3, 4, 5]
numbers2 = [2, 3, 4, 5, 6]
numbers3 = [3, 4, 5, 6, 7]


def test_single_message_serialisation_to_json():
    entity1 = SimpleTypeEntity(name="Event One", numbers=numbers1)
    marshall = Marshall()
    assert marshall.to_json(entity1) == json.dumps(
        _make_simple_entity("Event One", numbers1)
    )


def test_single_message_deserialisation_from_json():
    marshall = Marshall()
    json_string = json.dumps(_make_simple_entity("Event One", numbers1))
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
            _make_simple_entity("Event One", numbers1),
            _make_simple_entity("Event Two", numbers2),
            _make_simple_entity("Event Three", numbers3),
        ]
    )


def test_sequence_of_messages_deserialised_from_json():
    marshall = Marshall()
    json_string = json.dumps(
        [
            _make_simple_entity("Event One", numbers1),
            _make_simple_entity("Event Two", numbers2),
            _make_simple_entity("Event Three", numbers3),
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
        _make_complex_entity("Value One", "Value Two")
    )


def test_complex_object_deserialised_from_json():
    json_string = json.dumps(_make_complex_entity("Value One", "Value Two"))
    marshall = Marshall()
    assert marshall.from_json(json_string) == ComplexTypeEntity(
        one=ValueType(name="Value One"), two=ValueType(name="Value Two")
    )


def test_entity_with_custom_datetime_codec_serialised_to_json():
    entity_name = "Entity One"
    dt1 = datetime(2020, 1, 2, 3, 4, 5, 123456)
    iso_dt1 = "2020-01-02T03:04:05.123456"
    entity1 = CustomTypeEntity(name=entity_name, timestamp=dt1)
    marshall = Marshall()
    marshall.register_codec(fcn="eventz.marshall.DatetimeCodec", codec=DatetimeCodec())
    assert marshall.to_json(entity1) == json.dumps(
        _make_with_datetime_dict(name=entity_name, iso_dt=iso_dt1)
    )


def test_custom_datetime_codec_raises_error_with_wrong_type():
    entity1 = CustomTypeEntity(name="Entity One", timestamp="2020-01-02T03:04:05.123456")
    codec = DatetimeCodec()
    with pytest.raises(TypeError):
        codec.serialise(entity1)


def test_entity_with_custom_datetime_codec_deserialised_from_json():
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
    json_data = {"__fcn__": "tests.test_marshall.JsonSerialisableEntity", "public": 123}
    marshall = Marshall()
    assert marshall.from_json(json.dumps(json_data)) == JsonSerialisableEntity(
        public=value
    )


def test_mapping_to_json():
    entity = MappingEntity(
        mapping=immutables.Map(a=1, b=2)
    )
    json_data = {"__fcn__": "tests.test_marshall.MappingEntity", "mapping": {"a": 1, "b": 2}}
    marshall = Marshall()
    assert marshall.to_json(entity) == json.dumps(json_data)


def test_mapping_from_json():
    mapping = {"a": 1, "b": 2}
    json_data = {"__fcn__": "tests.test_marshall.MappingEntity", "mapping": mapping}
    marshall = Marshall()
    assert marshall.from_json(json.dumps(json_data)) == MappingEntity(
        mapping=immutables.Map(mapping)
    )


def test_enum_to_json():
    entity = EnumEntity(option=Option.TWO)
    json_data = {
        "__fcn__": "tests.test_marshall.EnumEntity",
        "option": {"__fcn__": "tests.test_marshall.Option", "_value_": 2, "_name_": "TWO",},
    }
    marshall = Marshall()
    assert marshall.to_json(entity) == json.dumps(json_data, sort_keys=True)


def test_enum_from_json():
    json_data = {
        "__fcn__": "tests.test_marshall.EnumEntity",
        "option": {"__fcn__": "tests.test_marshall.Option", "_value_": 2, "_name_": "TWO",},
    }
    marshall = Marshall()
    assert marshall.from_json(json.dumps(json_data)) == EnumEntity(option=Option.TWO)


def test_code_deregistration():
    marshall = Marshall()
    fcn = "eventz.marshall.DatetimeCodec"
    marshall.register_codec(fcn=fcn, codec=DatetimeCodec())
    assert marshall.has_codec(fcn) is True
    marshall.deregister_codec(fcn)
    assert marshall.has_codec(fcn) is False


def _make_simple_entity(name, numbers):
    return {
        "__fcn__": "tests.test_marshall.SimpleTypeEntity",
        "name": name,
        "numbers": numbers,
    }


def _make_complex_entity(name1, name2):
    return {
        "__fcn__": "tests.test_marshall.ComplexTypeEntity",
        "one": {"__fcn__": "tests.test_marshall.ValueType", "name": name1,},
        "two": {"__fcn__": "tests.test_marshall.ValueType", "name": name2,},
    }


def _make_mapping_entity(name1, name2):
    return {
        "__fcn__": "tests.test_marshall.MappingEntity",
        "mapping": {"one": 1, "two": 2,},
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
