from datetime import datetime
from typing import Optional

import immutables

from eventz.entity import Entity
from eventz.messages import Event, RoleOptions
from tests.example.children import Children
from tests.test_value_object import Child


class Parent(Entity):
    pass


class ParentCreated(Event):
    __version__: int = 1

    def __init__(
        self,
        aggregate_id: str,
        children: Children,
        __options__: Optional[immutables.Map[str, RoleOptions]] = None,
        __msgid__: str = None,
        __timestamp__: datetime = None,
        __seq__: Optional[int] = None,
    ):
        super().__init__(aggregate_id, __options__, __msgid__, __timestamp__, __seq__)
        self.children: Children = children


class ChildChosen(Event):
    __version__: int = 1

    def __init__(
        self,
        aggregate_id: str,
        child: Child,
        __options__: Optional[immutables.Map[str, RoleOptions]] = None,
        __msgid__: str = None,
        __timestamp__: datetime = None,
        __seq__: Optional[int] = None,
    ):
        super().__init__(aggregate_id, __options__, __msgid__, __timestamp__, __seq__)
        self.child: Child = child
