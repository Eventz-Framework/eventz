from __future__ import annotations
from datetime import datetime
from typing import Optional, Tuple, cast

import immutables

from eventz.aggregate import Aggregate
from eventz.value_object import ValueObject


class Message(ValueObject):
    def __init__(
        self,
        aggregate_id: str,
        __msgid__: Optional[str] = None,
        __timestamp__: Optional[datetime] = None,
    ):
        try:
            getattr(self, "__version__")
        except AttributeError:
            err = (
                "Child classes of Message cannot be instantiated "
                "without a '__version__' attribute set on the class."
            )
            raise TypeError(err)
        self.aggregate_id: str = aggregate_id
        self.__msgid__: str = __msgid__ or Aggregate.make_id()
        self.__timestamp__: datetime = __timestamp__ or datetime.utcnow()


class RoleOptions(ValueObject):
    """
    A representation of a role, the subscribers given that role at present
    and the allowed commands that the role grants, e.g.:
        RoleOptions(
            role_name="Dealer",  # name of the role
            subscribers=("123456789"),  # subscribers assigned to the role
            allowed_commands=("ShuffleDeck", "Deal"),  # commands that the client may now issue
        )
    """
    def __init__(
        self,
        role_name: str,
        agents: Tuple[str, ...],
        allowed_actions: Tuple[str, ...],
    ):
        self.role_name: str = role_name
        self.agents: Tuple[str, ...] = agents
        self.allowed_actions: Tuple[str, ...] = allowed_actions


class Event(Message):
    def __init__(
        self,
        aggregate_id: str,
        __options__: Optional[immutables.Map[str, RoleOptions]],
        __msgid__: Optional[str] = None,
        __timestamp__: Optional[datetime] = None,
        __seq__: Optional[int] = None,
    ):
        super().__init__(aggregate_id, __msgid__, __timestamp__)
        self.__options__: immutables.Map[str, RoleOptions] = __options__
        self.__seq__: Optional[int] = __seq__

    def is_persisted(self) -> bool:
        return self.__seq__ is not None

    def sequence(self, seq) -> Event:
        return cast(Event, self._mutate("__seq__", seq))


class Command(Message):
    def __init__(
        self, aggregate_id: str, __agent__: str, __msgid__: str = None, __timestamp__: datetime = None,
    ):
        super().__init__(aggregate_id, __msgid__, __timestamp__)
        self.__agent__ = __agent__
