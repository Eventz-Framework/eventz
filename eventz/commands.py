from datetime import datetime
from typing import Optional

from eventz.messages import Command


class ReplayCommand(Command):
    __version__: int = 1

    def __init__(
        self,
        aggregate_id: str,
        from_seq: Optional[int] = None,
        __msgid__: str = None,
        __timestamp__: datetime = None,
    ):
        super().__init__(aggregate_id, __msgid__, __timestamp__)
        self.from_seq: Optional[int] = from_seq


class SnapshotCommand(Command):
    __version__: int = 1

    def __init__(
        self,
        aggregate_id: str,
        __msgid__: str = None,
        __timestamp__: datetime = None,
    ):
        super().__init__(aggregate_id, __msgid__, __timestamp__)
