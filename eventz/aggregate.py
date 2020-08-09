from typing import Optional

from eventz.entity import Entity


class Aggregate(Entity):
    """
    Currently a placeholder class where logic specific to root aggregate entities
    may be placed in the future.
    """
    def __init__(self, uuid: Optional[str] = None):
        super().__init__(uuid)

    @staticmethod
    def make_id() -> str:
        return Entity.make_id()
