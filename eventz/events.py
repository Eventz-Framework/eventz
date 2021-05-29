from datetime import datetime
from typing import Any, Dict, Optional

from eventz.messages import Event


class SnapshotEvent(Event):
    __version__: int = 1

    def __init__(
        self,
        aggregate_id: str,
        state: Dict[str, Any],
        __msgid__: str = None,
        __timestamp__: datetime = None,
        __seq__: Optional[int] = None,
    ):
        super().__init__(aggregate_id, __msgid__, __timestamp__, __seq__)
        self.state: Dict[str, Any] = state
