import datetime
import importlib
import json
from enum import Enum
from typing import Any, Dict

import immutables
from dateutil.parser import parse

from eventz.protocols import MarshallCodecProtocol, MarshallProtocol


class Marshall(MarshallProtocol):
    def __init__(self, codecs: Dict[str, MarshallCodecProtocol] = None):
        self._codecs = {} if codecs is None else codecs

    def register_codec(self, fcn: str, codec: MarshallCodecProtocol):
        self._codecs[fcn] = codec

    def deregister_codec(self, fcn: str):
        del self._codecs[fcn]

    def has_codec(self, fcn: str):
        return fcn in self._codecs

    def to_json(self, data: Any) -> str:
        data = self._serialise_data(data)
        return json.dumps(data, sort_keys=True)

    def from_json(self, json_string: str) -> Any:
        data = json.loads(json_string)
        return self._deserialise_data(data)

    def _serialise_data(self, data: Any) -> Any:
        if self._is_handled_by_codec(data):
            return self._object_to_codec_dict(data)
        elif self._is_sequence(data):
            new_sequence = []
            for item in data:
                new_sequence.append(self._serialise_data(item))
            return new_sequence
        elif self._is_mapping(data):
            new_mapping = {}
            for key, value in data.items():
                new_mapping[key] = self._serialise_data(value)
            return new_mapping
        elif self._is_simple_type(data):
            return data
        else:
            return self._object_to_dict(data)

    def _deserialise_data(self, data: Any) -> Any:
        if self._is_enum_dict(data):
            return self._dict_to_enum(data)
        if self._is_serialised_class(data):
            return self._dict_to_object(data)
        elif self._requires_codec(data):
            return self._codec_dict_to_object(data)
        elif self._is_sequence(data):
            new_sequence = []
            for item in data:
                new_sequence.append(self._deserialise_data(item))
            return new_sequence
        elif self._is_mapping(data):
            new_mapping = {}
            for key, value in data.items():
                new_mapping[key] = self._deserialise_data(value)
            return immutables.Map(new_mapping)
        else:  # all other simple types now
            return data

    def _object_to_dict(self, obj: Any) -> Dict:
        data = {"__fcn__": self._get_fcn(obj)}
        if hasattr(obj, "version"):
            data["__version__"] = obj.version
        if hasattr(obj, "get_json_data") and callable(obj.get_json_data):
            json_data = obj.get_json_data()
        else:
            json_data = vars(obj)
        for attr, value in json_data.items():
            if not attr.startswith("__"):
                data[attr] = self._serialise_data(value)
        return data

    def _dict_to_object(self, data: Dict) -> Any:
        kwargs = {}
        for key, value in data.items():
            if not key.startswith("__"):
                kwargs[key] = self._deserialise_data(value)
        fully_qualified_name = data["__fcn__"]
        # @TODO add "allowed_namespaces" list to class and do a check here to protect against code injection
        _class = self._get_class_from_fcn(fully_qualified_name)
        return _class(**kwargs)

    def _codec_dict_to_object(self, data: Dict) -> Any:
        fcn = data["__codec__"]
        return self._codecs[fcn].deserialise(data["params"])

    def _object_to_codec_dict(self, obj: Any) -> Dict:
        for codec in self._codecs.values():
            if codec.handles(obj):
                return codec.serialise(obj)

    def _dict_to_enum(self, data: Dict) -> Enum:
        fully_qualified_name = data["__fcn__"]
        # @TODO add "allowed_namespaces" list to class and do a check here to protect against code injection
        _class = self._get_class_from_fcn(fully_qualified_name)
        return getattr(_class, data["_name_"])

    def _is_handled_by_codec(self, data: Any) -> bool:
        return any([codec.handles(data) for codec in self._codecs.values()])

    def _is_sequence(self, data: Any) -> bool:
        return isinstance(data, (list, tuple))

    def _is_mapping(self, data: Any) -> bool:
        return isinstance(data, (dict, set, immutables.Map))

    def _is_enum_dict(self, data: Dict) -> bool:
        return isinstance(data, Dict) and "_value_" in data and "_name_" in data

    def _is_simple_type(self, data: Any) -> bool:
        if type(data).__module__ == "builtins":
            return True
        # now check for any other types we want to treat as simple
        return isinstance(data, (datetime.datetime,))

    def _is_serialised_class(self, data: Any) -> bool:
        return isinstance(data, dict) and "__fcn__" in data

    def _requires_codec(self, data: Any) -> bool:
        return isinstance(data, dict) and "__codec__" in data

    def _get_fcn(self, obj):
        return obj.__class__.__module__ + "." + obj.__class__.__name__

    def _get_class_from_fcn(self, fcn: str) -> type:
        module_name, class_name = fcn.rsplit(".", 1)
        return getattr(importlib.import_module(module_name), class_name)


class NoCodecError(Exception):
    pass


class DatetimeCodec(MarshallCodecProtocol):
    def serialise(self, obj: Any) -> Dict:
        if not isinstance(obj, datetime.datetime):
            err = (
                "Only objects of type 'datetime.datetime' "
                "can be handled by DatetimeHandler codec."
            )
            raise TypeError(err)
        return {
            "__codec__": "eventz.marshall.DatetimeCodec",
            "params": {"timestamp": obj.isoformat()},
        }

    def deserialise(self, params: Dict) -> Any:
        return parse(params["timestamp"])

    def handles(self, obj: Any) -> bool:
        return isinstance(obj, datetime.datetime)
