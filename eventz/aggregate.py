from __future__ import annotations

from typing import Optional

from eventz.entity import Entity


class Aggregate(Entity):
    """
    Top-level entity that other services interact with from outside the domain.
    """

    def __init__(self, uuid: Optional[str] = None):
        super().__init__(uuid)

    @staticmethod
    def make_id() -> str:
        return Entity.make_id()
