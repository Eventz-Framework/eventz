from datetime import datetime
from typing import Optional

import immutables
import pytest

from eventz.aggregate import Aggregate
from eventz.messages import Event, RoleOptions


class NoVersion(Event):
    def __init__(
        self,
        aggregate_id: str,
        __options__: Optional[immutables.Map[str, RoleOptions]] = None,
        __msgid__: Optional[str] = None,
        __timestamp__: Optional[datetime] = None,
        __seq__: Optional[Optional[int]] = None,
    ):
        super().__init__(aggregate_id, __options__, __msgid__, __timestamp__, __seq__)


class Example(Event):
    __version__: int = 1

    def __init__(
        self,
        aggregate_id: str,
        __options__: Optional[immutables.Map[str, RoleOptions]] = None,
        __msgid__: Optional[str] = None,
        __timestamp__: Optional[datetime] = None,
        __seq__: Optional[Optional[int]] = None,
    ):
        super().__init__(aggregate_id, __options__, __msgid__, __timestamp__, __seq__)


def test_a_message_must_always_have_a_schema_version_set_on_the_class():
    with pytest.raises(TypeError):
        assert NoVersion(aggregate_id=Aggregate.make_id())
    example_event_message = Example(aggregate_id=Aggregate.make_id())
    assert example_event_message.__version__ == 1
