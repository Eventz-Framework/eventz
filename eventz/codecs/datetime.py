from datetime import datetime, timezone
from typing import Any, Dict

from dateutil.parser import parse

from eventz.protocols import MarshallCodecProtocol, MarshallProtocol


class Datetime(MarshallCodecProtocol):
    def serialise(self, obj: Any, marshall: MarshallProtocol) -> Dict:
        if not isinstance(obj, datetime):
            err = (
                "Only objects of type 'datetime.datetime' "
                "can be handled by DatetimeHandler codec."
            )
            raise TypeError(err)
        return {
            "__codec__": "codecs.eventz.Datetime",
            "params": {"timestamp": self._iso_js_format(obj)},
        }

    def deserialise(self, params: Dict, marshall: MarshallProtocol) -> Any:
        return parse(params["timestamp"])

    def handles(self, obj: Any) -> bool:
        return isinstance(obj, datetime)

    def _iso_js_format(self, dt: datetime) -> str:
        return (
            dt.astimezone(timezone.utc)
            .isoformat(timespec="milliseconds")
            .replace("+00:00", "Z")
        )
