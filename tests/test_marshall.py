import json
from datetime import datetime
from enum import Enum
from typing import List, Dict

import immutables
import pytest

from eventz.marshall import Marshall, DatetimeCodec, FqnResolver
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

resolver = FqnResolver(fqn_map={"tests.*": "tests.test_marshall.*"})
marshall = Marshall(fqn_resolver=resolver)


def test_fqn_map_resolution():
    entity1 = SimpleTypeEntity(name="Event One", numbers=numbers1)
    value_type1 = ValueType(name="One")
    resolver = FqnResolver(
        fqn_map={
            "tests.SimpleTypeEntity": "tests.test_marshall.SimpleTypeEntity",
            "tests.ValueType": "tests.test_marshall.ValueType",
        }
    )
    assert resolver.instance_to_fqn(entity1) == "tests.SimpleTypeEntity"
    assert resolver.instance_to_fqn(value_type1) == "tests.ValueType"
    assert resolver.fqn_to_type("tests.SimpleTypeEntity") == SimpleTypeEntity
    assert resolver.fqn_to_type("tests.ValueType") == ValueType
    resolver = FqnResolver(fqn_map={"tests.*": "tests.test_marshall.*"})
    assert resolver.instance_to_fqn(entity1) == "tests.SimpleTypeEntity"
    assert resolver.instance_to_fqn(value_type1) == "tests.ValueType"
    assert resolver.fqn_to_type("tests.SimpleTypeEntity") == SimpleTypeEntity
    assert resolver.fqn_to_type("tests.ValueType") == ValueType


def test_single_message_serialisation_to_json():
    entity1 = SimpleTypeEntity(name="Event One", numbers=numbers1)
    assert marshall.to_json(entity1) == (
        '{"__fqn__":"tests.SimpleTypeEntity",'
        '"name":"Event One",'
        '"numbers":[1,2,3,4,5]}'
    )


def test_single_message_deserialisation_from_json():
    json_string = (
        '{"__fqn__":"tests.SimpleTypeEntity",'
        '"name":"Event One",'
        '"numbers":[1,2,3,4,5]}'
    )
    assert marshall.from_json(json_string) == SimpleTypeEntity(
        name="Event One", numbers=numbers1
    )


def test_sequence_of_messages_serialised_to_json():
    list_of_entities = [
        SimpleTypeEntity(name="Event One", numbers=numbers1),
        SimpleTypeEntity(name="Event Two", numbers=numbers2),
        SimpleTypeEntity(name="Event Three", numbers=numbers3),
    ]
    assert marshall.to_json(list_of_entities) == (
        "["
        '{"__fqn__":"tests.SimpleTypeEntity",'
        '"name":"Event One",'
        '"numbers":[1,2,3,4,5]},'
        '{"__fqn__":"tests.SimpleTypeEntity",'
        '"name":"Event Two",'
        '"numbers":[2,3,4,5,6]},'
        '{"__fqn__":"tests.SimpleTypeEntity",'
        '"name":"Event Three",'
        '"numbers":[3,4,5,6,7]}'
        "]"
    )


def test_sequence_of_messages_deserialised_from_json():
    json_string = (
        "["
        '{"__fqn__":"tests.SimpleTypeEntity",'
        '"name":"Event One",'
        '"numbers":[1,2,3,4,5]},'
        '{"__fqn__":"tests.SimpleTypeEntity",'
        '"name":"Event Two",'
        '"numbers":[2,3,4,5,6]},'
        '{"__fqn__":"tests.SimpleTypeEntity",'
        '"name":"Event Three",'
        '"numbers":[3,4,5,6,7]}'
        "]"
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
    assert marshall.to_json(entity1) == (
        "{"
        '"__fqn__":"tests.ComplexTypeEntity",'
        '"one":{"__fqn__":"tests.ValueType","name":"Value One"},'
        '"two":{"__fqn__":"tests.ValueType","name":"Value Two"}'
        "}"
    )


def test_complex_object_deserialised_from_json():
    json_string = (
        "{"
        '"__fqn__":"tests.ComplexTypeEntity",'
        '"one":{"__fqn__":"tests.ValueType","name":"Value One"},'
        '"two":{"__fqn__":"tests.ValueType","name":"Value Two"}'
        "}"
    )
    assert marshall.from_json(json_string) == ComplexTypeEntity(
        one=ValueType(name="Value One"), two=ValueType(name="Value Two")
    )


def test_entity_with_custom_datetime_codec_serialised_to_json():
    entity_name = "Entity One"
    dt1 = datetime(2020, 1, 2, 3, 4, 5, 123456)
    entity1 = CustomTypeEntity(name=entity_name, timestamp=dt1)
    marshall.register_codec(fcn="eventz.marshall.DatetimeCodec", codec=DatetimeCodec())
    assert marshall.to_json(entity1) == (
        "{"
        '"__fqn__":"tests.CustomTypeEntity",'
        '"name":"Entity One",'
        '"timestamp":{'
        '"__codec__":"eventz.marshall.DatetimeCodec",'
        '"params":{"timestamp":"2020-01-02T03:04:05.123456"}'
        "}"
        "}"
    )


def test_custom_datetime_codec_raises_error_with_wrong_type():
    entity1 = CustomTypeEntity(
        name="Entity One", timestamp="2020-01-02T03:04:05.123456"
    )
    codec = DatetimeCodec()
    with pytest.raises(TypeError):
        codec.serialise(entity1)


def test_entity_with_custom_datetime_codec_deserialised_from_json():
    entity_name = "Entity One"
    dt1 = datetime(2020, 1, 2, 3, 4, 5, 123456)
    json_string = (
        "{"
        '"__fqn__":"tests.CustomTypeEntity",'
        '"name":"Entity One",'
        '"timestamp":{'
        '"__codec__":"eventz.marshall.DatetimeCodec",'
        '"params":{"timestamp":"2020-01-02T03:04:05.123456"}'
        "}"
        "}"
    )
    marshall.register_codec(fcn="eventz.marshall.DatetimeCodec", codec=DatetimeCodec())
    assert marshall.from_json(json_string) == CustomTypeEntity(
        name=entity_name, timestamp=dt1
    )


def test_json_serialisable_class_to_json():
    value = 123
    entity = JsonSerialisableEntity(public=value)
    assert (
        marshall.to_json(entity)
        == '{"__fqn__":"tests.JsonSerialisableEntity","public":123}'
    )


def test_json_serialisable_class_from_json():
    value = 123
    json_data = {"__fqn__": "tests.JsonSerialisableEntity", "public": 123}
    assert marshall.from_json(json.dumps(json_data)) == JsonSerialisableEntity(
        public=value
    )


def test_mapping_to_json():
    entity = MappingEntity(mapping=immutables.Map(a=1, b=2))
    assert marshall.to_json(entity) == (
        "{" '"__fqn__":"tests.MappingEntity",' '"mapping":{"a":1,"b":2}' "}"
    )


def test_mapping_from_json():
    mapping = {"a": 1, "b": 2}
    json_data = {"__fqn__": "tests.MappingEntity", "mapping": mapping}
    assert marshall.from_json(json.dumps(json_data)) == MappingEntity(
        mapping=immutables.Map(mapping)
    )


def test_enum_to_json():
    entity = EnumEntity(option=Option.TWO)
    assert marshall.to_json(entity) == (
        "{"
        '"__fqn__":"tests.EnumEntity",'
        '"option":{"__fqn__":"tests.Option","_name_":"TWO","_value_":2}'
        "}"
    )


def test_enum_from_json():
    json_data = {
        "__fqn__": "tests.EnumEntity",
        "option": {"__fqn__": "tests.Option", "_value_": 2, "_name_": "TWO",},
    }
    assert marshall.from_json(json.dumps(json_data)) == EnumEntity(option=Option.TWO)


def test_code_deregistration():
    fcn = "eventz.marshall.DatetimeCodec"
    marshall.register_codec(fcn=fcn, codec=DatetimeCodec())
    assert marshall.has_codec(fcn) is True
    marshall.deregister_codec(fcn)
    assert marshall.has_codec(fcn) is False


def _make_mapping_entity(name1, name2):
    return {
        "__fqn__": "tests.MappingEntity",
        "mapping": {"one": 1, "two": 2,},
    }
