import json
from datetime import datetime, timezone
from enum import Enum
from typing import List, Dict

import immutables
import pytest
import stringcase

from eventz.marshall import Marshall, FqnResolver, transform_keys
from eventz.codecs.datetime import Datetime
from eventz.packets import Packet
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


class LongNamedEntity(ValueObject):
    def __init__(
        self, one_two_three: str
    ):
        self.one_two_three: str = one_two_three


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

resolver = FqnResolver(fqn_map={
    "tests.*": "tests.test_marshall.*",
    "eventz.packets.*": "eventz.packets.*",
})
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
    marshall.register_codec(fcn="codecs.eventz.Datetime", codec=Datetime())
    entity1 = CustomTypeEntity(
        name="Entity One",
        timestamp=datetime(2020, 1, 2, 3, 4, 5, 123456)
    )
    assert marshall.to_json(entity1) == (
        "{"
        '"__fqn__":"tests.CustomTypeEntity",'
        '"name":"Entity One",'
        '"timestamp":{'
        '"__codec__":"codecs.eventz.Datetime",'
        '"params":{"timestamp":"2020-01-02T03:04:05.123Z"}'
        "}"
        "}"
    )
    entity2 = CustomTypeEntity(
        name="Entity Two",
        timestamp=datetime(2020, 1, 2, 3, 4, 5)
    )
    assert marshall.to_json(entity2) == (
        "{"
        '"__fqn__":"tests.CustomTypeEntity",'
        '"name":"Entity Two",'
        '"timestamp":{'
        '"__codec__":"codecs.eventz.Datetime",'
        '"params":{"timestamp":"2020-01-02T03:04:05.000Z"}'
        "}"
        "}"
    )
    entity3 = CustomTypeEntity(
        name="Entity Three",
        timestamp=datetime(2020, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
    )
    assert marshall.to_json(entity3) == (
        "{"
        '"__fqn__":"tests.CustomTypeEntity",'
        '"name":"Entity Three",'
        '"timestamp":{'
        '"__codec__":"codecs.eventz.Datetime",'
        '"params":{"timestamp":"2020-01-02T03:04:05.000Z"}'
        "}"
        "}"
    )


def test_custom_datetime_codec_raises_error_with_wrong_type():
    entity1 = CustomTypeEntity(
        name="Entity One", timestamp="2020-01-02T03:04:05.123Z"
    )
    codec = Datetime()
    with pytest.raises(TypeError):
        codec.serialise(entity1)


def test_entity_with_custom_datetime_codec_deserialised_from_json():
    json_string = (
        "{"
        '"__fqn__":"tests.CustomTypeEntity",'
        '"name":"Entity One",'
        '"timestamp":{'
        '"__codec__":"codecs.eventz.Datetime",'
        '"params":{"timestamp":"2020-01-02T03:04:05.123Z"}'
        "}"
        "}"
    )
    marshall.register_codec(fcn="codecs.eventz.Datetime", codec=Datetime())
    assert marshall.from_json(json_string) == CustomTypeEntity(
        name="Entity One",
        timestamp=datetime(2020, 1, 2, 3, 4, 5, 123000, tzinfo=timezone.utc)
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


def test_transformation_of_json_keys():
    transform_func = getattr(stringcase, "camelcase")
    assert transform_keys({"one": 1, "two_three": 23}, transform_func) == {
        "one": 1,
        "twoThree": 23,
    }
    assert transform_keys(
        {"one": [{"four_five": 45, "six_seven": 67}], "two_three": 23}, transform_func
    ) == {"one": [{"fourFive": 45, "sixSeven": 67}], "twoThree": 23}
    assert transform_keys({"__fcn__": "Shouldn't change"}, transform_func) == {
        "__fcn__": "Shouldn't change"
    }


def test_serialising_to_camel_case():
    entity = LongNamedEntity(
        one_two_three="Value",
    )
    assert marshall.to_json(entity) == (
        "{"
        '"__fqn__":"tests.LongNamedEntity",'
        '"oneTwoThree":"Value"'
        "}"
    )


def test_serialising_to_snake_case():
    json_string =  (
        "{"
        '"__fqn__":"tests.LongNamedEntity",'
        '"oneTwoThree":"Value"'
        "}"
    )
    assert marshall.from_json(json_string) == LongNamedEntity(
        one_two_three="Value",
    )


def test_mapping_with_preserve_keys_does_not_get_modified():
    json_string = (
        "{"
        '"Key Name":"example",'
        '"__preserve_keys__":true'
        "}"
    )
    mapping_example = immutables.Map({'__preserve_keys__': True, 'Key Name': 'example'})
    assert marshall.from_json(json_string) == mapping_example
    assert marshall.to_json(mapping_example) == json_string


def test_code_deregistration():
    fcn = "codecs.eventz.Datetime"
    marshall.register_codec(fcn=fcn, codec=Datetime())
    assert marshall.has_codec(fcn) is True
    marshall.deregister_codec(fcn)
    assert marshall.has_codec(fcn) is False


def test_serialisation_of_packets():
    packet = Packet(
        subscribers=["a1b2c3d4"],
        message_type="EVENT",
        route="ExampleService",
        msgid="11111111",
        dialog="22222222",
        seq=2,
        payload={
            "one": 1,
            "two": 2,
        }
    )
    assert (
        '{'
            '"__fqn__":"eventz.packets.Packet",'
            '"dialog":"22222222",'
            '"messageType":"EVENT",'
            '"msgid":"11111111",'
            '"payload":{"one":1,"two":2},'
            '"route":"ExampleService",'
            '"seq":2,'
            '"subscribers":["a1b2c3d4"]'
        '}'
    ) == marshall.to_json(packet)


def _make_mapping_entity(name1, name2):
    return {
        "__fqn__": "tests.MappingEntity",
        "mapping": {"one": 1, "two": 2,},
    }
