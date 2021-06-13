from datetime import datetime
from typing import Any, Dict, List, Optional

import immutables

from eventz.messages import Event, RoleOptions


class SnapshotEvent(Event):
    __version__: int = 1

    def __init__(
        self,
        aggregate_id: str,
        state: Dict[str, Any],
        order: List[str],
        __options__: Optional[immutables.Map[str, RoleOptions]] = None,
        __msgid__: Optional[str] = None,
        __timestamp__: Optional[datetime] = None,
        __seq__: Optional[int] = None,
    ):
        super().__init__(aggregate_id, __options__, __msgid__, __timestamp__, __seq__)
        self.state: Dict[str, Any] = state
        self.order: List[str] = order
