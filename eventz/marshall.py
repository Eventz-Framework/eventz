from __future__ import annotations

import datetime
import importlib
import json
import logging
import os
from collections import Mapping
from enum import Enum
from typing import Any, Dict, Optional, Callable

import immutables
import stringcase

from eventz.protocols import MarshallCodecProtocol, MarshallProtocol

log = logging.getLogger(__name__)
log.setLevel(os.getenv("LOG_LEVEL", "DEBUG"))


class Marshall(MarshallProtocol):
    def __init__(
        self,
        fqn_resolver: FqnResolverProtocol,
        codecs: Dict[str, MarshallCodecProtocol] = None,
        serialisation_case: Optional[str] = "camelcase",
        deserialisation_case: Optional[str] = "snakecase",
    ):
        self._fqn_resolver: FqnResolverProtocol = fqn_resolver
        self._codecs = {} if codecs is None else codecs
        self._serialisation_func: Callable[[str], str] = getattr(
            stringcase, serialisation_case
        )
        self._deserialisation_func: Callable[[str], str] = getattr(
            stringcase, deserialisation_case
        )

    def register_codec(self, fcn: str, codec: MarshallCodecProtocol):
        self._codecs[fcn] = codec

    def deregister_codec(self, fcn: str):
        del self._codecs[fcn]

    def has_codec(self, fcn: str):
        return fcn in self._codecs

    def to_json(self, data: Any) -> str:
        data = self.serialise_data(data)
        data = self.transform_keys_serialisation(data)
        log.debug(f"Marshall.to_json data={data}")
        return json.dumps(data, sort_keys=True, separators=(",", ":"))

    def from_json(self, json_string: str) -> Any:
        data = json.loads(json_string)
        data = self.transform_keys_deserialisation(data)
        log.debug(f"Marshall.from_json data={data}")
        return self.deserialise_data(data)

    def transform_keys_serialisation(self, data):
        return transform_keys(data, self._serialisation_func)

    def transform_keys_deserialisation(self, data):
        return transform_keys(data, self._deserialisation_func)

    def serialise_data(self, data: Any) -> Any:
        if self._is_handled_by_codec(data):
            return self._object_to_codec_dict(data)
        elif self._is_sequence(data):
            new_sequence = []
            for item in data:
                new_sequence.append(self.serialise_data(item))
            return new_sequence
        elif self._is_mapping(data):
            new_mapping = {}
            for key, value in data.items():
                new_mapping[key] = self.serialise_data(value)
            return new_mapping
        elif self._is_simple_type(data):
            return data
        else:
            return self._object_to_dict(data)

    def deserialise_data(self, data: Any) -> Any:
        if self._is_enum_dict(data):
            return self._dict_to_enum(data)
        if self._is_serialised_class(data):
            return self._dict_to_object(data)
        elif self._requires_codec(data):
            return self._codec_dict_to_object(data)
        elif self._is_sequence(data):
            new_sequence = []
            for item in data:
                new_sequence.append(self.deserialise_data(item))
            return new_sequence
        elif self._is_mapping(data):
            new_mapping = {}
            for key, value in data.items():
                new_mapping[key] = self.deserialise_data(value)
            return immutables.Map(new_mapping)
        else:  # all other simple types now
            return data

    def _object_to_dict(self, obj: Any) -> Dict:
        data = {
            "__fqn__": self._fqn_resolver.instance_to_fqn(obj)
        }
        if hasattr(obj, "__version__"):
            data["__version__"] = obj.__version__
        if hasattr(obj, "__msgid__"):
            data["__msgid__"] = obj.__msgid__
        if hasattr(obj, "__timestamp__"):
            data["__timestamp__"] = self.serialise_data(obj.__timestamp__)
        if hasattr(obj, "get_json_data") and callable(obj.get_json_data):
            json_data = obj.get_json_data()
        else:
            json_data = vars(obj)
        for attr, value in json_data.items():
            if not attr.startswith("__"):
                data[attr] = self.serialise_data(value)
        return data

    def _dict_to_object(self, data: Dict) -> Any:
        kwargs = {}
        if data.get("__msgid__"):
            kwargs["__msgid__"] = data.get("__msgid__")
        if data.get("__timestamp__"):
            kwargs["__timestamp__"] = self.deserialise_data(data.get("__timestamp__"))
        for key, value in data.items():
            if not key.startswith("__"):
                kwargs[key] = self.deserialise_data(value)
        # @TODO add "allowed_namespaces" list to class and do a check here to protect against code injection
        _class = self._fqn_resolver.fqn_to_type(data["__fqn__"])
        return _class(**kwargs)

    def _codec_dict_to_object(self, data: Dict) -> Any:
        log.debug(f"Marshall._dict_to_object data={data}")
        fcn = data["__codec__"]
        log.debug(f"Codec fcn={fcn}")
        codec = self._codecs[fcn].deserialise(data["params"])
        log.debug(f"codec={codec}")
        return codec

    def _object_to_codec_dict(self, obj: Any) -> Optional[Dict]:
        log.debug(f"Marshall._object_to_codec_dict obj={obj}")
        for codec in self._codecs.values():
            log.debug(f"...codec={codec}")
            if codec.handles(obj):
                log.debug("... Found codec to handle object.")
                dict_ = codec.serialise(obj)
                log.debug(f"Object serialised to: {dict_}")
                return dict_

    def _dict_to_enum(self, data: Dict) -> Enum:
        # @TODO add "allowed_namespaces" list to class and do a check here to protect against code injection
        _class = self._fqn_resolver.fqn_to_type(data["__fqn__"])
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
        return isinstance(data, dict) and "__fqn__" in data

    def _requires_codec(self, data: Any) -> bool:
        return isinstance(data, dict) and "__codec__" in data


class NoCodecError(Exception):
    pass


class FqnResolverProtocol:
    def fqn_to_type(self, fqn: str) -> type:
        ...

    def instance_to_fqn(self, instance: Any) -> str:
        ...


class FqnResolver(FqnResolverProtocol):
    def __init__(self, fqn_map: Dict):
        """
        The "public" side of the map is the fqn written into the JSON payloads.
        The "private" side of the map is whatever path is needed to help the
        client code transform the fqn into an instance.
        """
        log.debug(f"FqnResolver initialised with fqn_map={fqn_map}")
        self._public_to_private: Dict = fqn_map
        self._private_to_public: Dict = {b: a for a, b in fqn_map.items()}

    def fqn_to_type(self, fqn: str) -> type:
        log.debug(f"FqnResolver.fqn_to_type fqn={fqn}")
        module_path = self._get_fqn(fqn, public=True)
        log.debug(f"module_path={module_path}")
        module_name, class_name = module_path.rsplit(".", 1)
        type_ = getattr(importlib.import_module(module_name), class_name)
        log.debug(f"module_path resloved to type={type_}")
        return type_

    def instance_to_fqn(self, instance: Any) -> str:
        log.debug(f"FqnResolver.instance_to_fqn instance={instance}")
        path = instance.__class__.__module__ + "." + instance.__class__.__name__
        log.debug(f"path={path}")
        fqn = self._get_fqn(path, public=False)
        log.debug(f"path rresolved to fqn={fqn}")
        return fqn

    def _get_fqn(self, key: str, public: bool) -> str:
        log.debug(f"FqnResolver._get_fqn key={key} public={public}")
        try:
            return self._lookup_fqn(key, public)
        except KeyError as e:
            # can we resolve with * path?
            if key[-1] != "*" and "." in key:
                parts = key.split(".")
                entity = parts.pop()
                star_key = ".".join(parts + ["*"])
                log.debug(f"entity={entity} star_key={star_key}")
                path = self._lookup_fqn(star_key, public)
                log.debug(f"path={path}")
                path_without_star = path[:-1]
                resolved_fqn = path_without_star + entity
                log.debug(f"resolved_fqn={resolved_fqn}")
                return resolved_fqn
            raise e

    def _lookup_fqn(self, key: str, public: bool) -> str:
        if public:
            return self._public_to_private[key]
        else:
            return self._private_to_public[key]


def transform_keys(input: Any, func: Callable[[str], str]) -> Any:
    if isinstance(input, dict):
        new_dict = {}
        for k, v in input.items():
            if not k.startswith("__"):
                k = func(k)
            new_dict[k] = transform_keys(v, func)
        return new_dict
    elif isinstance(input, list):
        new_list = []
        for v in input:
            new_list.append(transform_keys(v, func))
        return new_list
    else:
        return input
