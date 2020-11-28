import datetime
from typing import Any, Dict

from dateutil.parser import parse

from eventz.protocols import MarshallCodecProtocol


class Datetime(MarshallCodecProtocol):
    def serialise(self, obj: Any) -> Dict:
        if not isinstance(obj, datetime.datetime):
            err = (
                "Only objects of type 'datetime.datetime' "
                "can be handled by DatetimeHandler codec."
            )
            raise TypeError(err)
        return {
            "__codec__": "codecs.eventz.Datetime",
            "params": {"timestamp": obj.isoformat()},
        }

    def deserialise(self, params: Dict) -> Any:
        return parse(params["timestamp"])

    def handles(self, obj: Any) -> bool:
        return isinstance(obj, datetime.datetime)
